# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple
from itertools import groupby

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sale_ids = fields.Many2many("sale.order", compute="_compute_sale_ids", store=True)
    # don't copy the printed state of a picking otherwise the backorder of a
    # printed picking becomes printed
    printed = fields.Boolean(copy=False)
    canceled_by_merge = fields.Boolean(
        default=False,
        help="Technical field. Indicates the transfer is"
        " canceled because it was left empty after a manual merge.",
    )

    @api.depends("canceled_by_merge")
    def _compute_state(self):
        super()._compute_state()
        for picking in self:
            if picking.canceled_by_merge:
                picking.state = "cancel"

    def _check_emptyness_after_merge(self):
        """Handle pickings emptied during a manual merge."""
        for picking in self:
            if not picking.move_lines:
                picking.canceled_by_merge = True

    @api.depends("move_lines.group_id.sale_ids")
    def _compute_sale_ids(self):
        for rec in self:
            rec.sale_ids = rec.mapped("move_lines.group_id.sale_ids")

    def write(self, values):
        if self.env.context.get("picking_no_overwrite_partner_origin"):
            written_fields = set(values.keys())
            if written_fields == {"partner_id", "origin"}:
                values = {}
        return super().write(values)

    def action_cancel(self):
        cancel_sale_id = self.env.context.get("cancel_sale_id")
        if cancel_sale_id:
            moves = self.move_lines.filtered(
                lambda m: cancel_sale_id in m.original_group_id.sale_ids.ids
                and m.state not in ("done", "cancel")
            )
            moves.with_context(cancel_sale_id=False)._action_cancel()
            return True
        else:
            return super().action_cancel()

    def _create_backorder(self):
        self = self.with_context(picking_no_copy_if_can_group=1)
        backorders = super()._create_backorder()
        backorders._merge_procurement_groups()
        return backorders

    def _prepare_merge_procurement_group_values(self, move_groups):
        sales = move_groups.sale_id
        return {
            "sale_ids": [(6, 0, sales.ids)],
            "name": ", ".join(move_groups.mapped("name")),
        }

    def _merge_procurement_groups(self):
        for picking in self:
            if not picking.picking_type_id.group_pickings:
                continue
            if picking.picking_type_id.code != "outgoing":
                continue
            base_group = picking.group_id
            # If we have different sales in the line's group, it means moves
            # have been merged in the same picking/group but they come from a
            # different sale.
            moves = picking.move_lines
            moves_groups = moves.original_group_id
            moves_sales = moves_groups.sale_id
            group_sales = base_group.sale_ids
            # if we have different sales, it means "_assign_picking" added
            # moves from another SO in the picking
            if moves_sales != group_sales:
                # create a new joint group for the existing different groups
                new_group = base_group.copy(
                    self._prepare_merge_procurement_group_values(moves_groups)
                )
                pickings = base_group.picking_ids.filtered(
                    lambda picking: picking.picking_type_id.group_pickings
                    # Do no longer modify a printed or done transfer: they are
                    # started and their group is now fixed. It prevents keeping
                    # old, done sales orders in new groups forever
                    and not (picking.printed or picking.state == "done")
                )
                pickings.move_lines.group_id = new_group

    def copy(self, defaults=None):
        if self.env.context.get("picking_no_copy_if_can_group") and self.move_lines:
            # we are in the process of the creation of a backorder. If we can
            # find a suitable picking, then use it instead of copying the one
            # we are creating a backorder from
            picking = self.move_lines[0]._search_picking_for_assignation()
            if picking:
                return picking
        return super(
            StockPicking, self.with_context(picking_no_copy_if_can_group=0)
        ).copy(defaults)

    def get_delivery_report_lines(self):
        self.ensure_one()
        if self.state != "done":
            moves = self.move_lines.filtered("product_uom_qty").sorted(
                lambda m: m.sale_line_id.order_id
            )
            if len(moves.mapped("sale_line_id.order_id")) > 1:
                sales_and_moves = []
                for sale, sale_moves in groupby(
                    moves, lambda m: m.sale_line_id.order_id
                ):
                    sales_and_moves.append(
                        MockedMove(
                            product_id=False,
                            description_picking=sale.get_name_for_delivery_line(),
                            product_uom_qty=0,
                            product_uom=False,
                            lot_name="",
                        )
                    )
                    for move in sale_moves:
                        sales_and_moves.append(move)
                return sales_and_moves
            else:
                return moves
        else:
            moves = self.move_lines.sorted(lambda m: m.sale_line_id.order_id)
            if len(moves.mapped("sale_line_id.order_id")) > 1:
                sales_and_moves = []
                for sale, sale_moves in groupby(
                    moves, lambda m: m.sale_line_id.order_id
                ):
                    sales_and_moves.append(
                        MockedMove(
                            product_id=False,
                            description_picking=sale.get_name_for_delivery_line(),
                            product_uom_qty=0,
                            product_uom=False,
                            lot_name="",
                        )
                    )
                    for move in sale_moves:
                        for move_line in move.move_line_ids:
                            sales_and_moves.append(move_line)
                return sales_and_moves
            else:
                return self.move_line_ids

    def get_customer_refs(self):
        """Returns all unique sales order customer references."""
        if self.state != "done":
            move_lines = self.move_lines.filtered("product_uom_qty")
        else:
            move_lines = self.move_lines
        references = move_lines.mapped("sale_line_id.order_id.client_order_ref")
        return set(filter(None, references))


MockedMove = namedtuple(
    "MockedMove",
    ["product_id", "description_picking", "product_uom_qty", "product_uom", "lot_name"],
)
