# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        res = super()._compute_state()
        for picking in self:
            if picking.canceled_by_merge:
                picking.state = "cancel"
        return res

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
        # When a SO is canceled, cancel only moves related to this SO and not
        # all moves of the picking
        cancel_sale_group_ids = self.env.context.get("cancel_sale_group_ids")
        if cancel_sale_group_ids:
            moves = self.move_lines.filtered(
                lambda m: m.original_group_id.id in cancel_sale_group_ids
                and m.state not in ("done", "cancel")
            )
            moves.with_context(cancel_sale_group_ids=False)._action_cancel()
            return True
        else:
            return super().action_cancel()

    def _create_backorder(self):
        backorders = self.browse()
        for picking in self:
            if not picking._is_grouping_disabled():
                picking = picking.with_context(picking_no_copy_if_can_group=1)
            backorder = super(StockPicking, picking)._create_backorder()
            if backorder and not picking._is_grouping_disabled():
                backorder._merge_procurement_groups()
                backorder._update_merged_origin()
            backorders |= backorder
        return backorders

    def _prepare_merged_origin(self):
        """Concatenate all origin together.
        Note that in standard, only max 5 are displayed"""
        moves = self.move_lines.filtered(lambda m: m.state != "cancel")
        origins = moves.filtered(lambda m: m.origin).mapped("origin")
        origins = sorted(list(set(origins)))
        return " ".join(origins)

    def _update_merged_origin(self):
        self.origin = self._prepare_merged_origin()

    def _prepare_merge_procurement_group_values(self, move_groups):
        """Build a new procurement group that is the merge of given procurement
        group."""
        sales = move_groups.sale_id
        return {
            "sale_ids": [(6, 0, sales.ids)],
            "name": ", ".join(move_groups.sorted("name").mapped("name")),
        }

    def _merge_procurement_groups(self):
        self.ensure_one()
        if self._is_grouping_disabled():
            return False
        if self.picking_type_id.code != "outgoing":
            return False
        group_pickings = self.move_lines.group_id.picking_ids.filtered(
            # Do no longer modify a printed or done transfer: they are
            # started and their group is now fixed. It prevents keeping
            # old, done sales orders in new groups forever
            lambda picking: not (picking.printed or picking.state == "done")
        )
        moves = group_pickings.move_lines
        base_group = self.group_id

        # If we have moves of different procurement groups, it means moves
        # have been merged in the same picking. In this case a new
        # procurement group is required
        if len(moves.original_group_id) > 1 and base_group in moves.original_group_id:
            # Create a new procurement group
            new_group = base_group.copy(
                self._prepare_merge_procurement_group_values(moves.original_group_id)
            )
            group_pickings.move_lines.group_id = new_group
            return True

        new_moves = moves.filtered(lambda move: move.group_id != base_group)
        old_moves = moves - new_moves
        if new_moves.original_group_id - old_moves.original_group_id:
            # A move with a new procurement group has been added. Adapt
            # the procurement group
            closed_pickings = self.move_lines.group_id.picking_ids.filtered(
                lambda picking: picking.printed or picking.state == "done"
            )
            if closed_pickings:
                # Do no longer modify a printed or done transfer: they
                # are started and their group is now fixed. So create a
                # new procurement group
                new_group = base_group.copy(
                    self._prepare_merge_procurement_group_values(
                        moves.original_group_id
                    )
                )
                group_pickings.move_lines.group_id = new_group
                return True

            base_group.write(
                self._prepare_merge_procurement_group_values(moves.original_group_id)
            )
            new_moves.group_id = base_group
            return True
        new_moves.group_id = base_group
        return False

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

    def _is_grouping_disabled(self):
        self.ensure_one()
        return (
            not self.picking_type_id.group_pickings
            or self.partner_id.disable_picking_grouping
        )

    def _group_moves_by_order(self, moves):
        # Meant to be overridden
        return groupby(moves, lambda m: m.sale_line_id.order_id)

    def _get_sorted_moves(self):
        # Meant to be overriden
        self.ensure_one()
        moves = self.move_lines.filtered(lambda m: m.state != "cancel")
        return moves.sorted(lambda m: m.sale_line_id.order_id.id)

    def _get_sorted_move_lines(self):
        # Meant to be overriden
        self.ensure_one()
        return self.move_line_ids

    def _delivery_report_state_is_done(self):
        return self.state == "done"

    def get_delivery_report_lines(self):
        """Return the lines that will be on the report.

        If the picking concerns multiple sale order some fake records are
        inserted to have the sale information as line separators.
        Otherwise standard records are returned.
        """
        self.ensure_one()
        moves = self._get_sorted_moves()
        if not self._delivery_report_state_is_done():
            moves = moves.filtered("reserved_availability")

        if len(moves.mapped("sale_line_id.order_id")) > 1:
            grouped_moves = self._group_moves_by_order(moves)
            fake_record = {
                "product_id": 1,
                "product_uom_qty": 0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "company_id": self.env.user.company_id.id,
                "location_id": self.env.ref("stock.stock_location_output").id,
                "location_dest_id": self.env.ref("stock.stock_location_output").id,
            }
            if not self._delivery_report_state_is_done():
                sales_and_moves = self.env["stock.move"]
                fake_record["name"] = "fake move"
                for sale, sale_moves in grouped_moves:
                    line_desc = sale.get_name_for_delivery_line()
                    fake_record.update(
                        {"description_picking": line_desc, "origin": sale.name}
                    )
                    sales_and_moves |= sales_and_moves.new(fake_record.copy())
                    for move in sale_moves:
                        sales_and_moves |= move
                return sales_and_moves
            else:
                sales_and_moves = self.env["stock.move.line"]
                fake_record["product_uom_id"] = fake_record.pop("product_uom")
                for sale, sale_moves in grouped_moves:
                    if sale:
                        line_desc = sale.get_name_for_delivery_line()
                        fake_record.update(
                            {"description_picking": line_desc, "origin": sale.name}
                        )
                        sales_and_moves |= sales_and_moves.new(fake_record.copy())
                    for move in sale_moves:
                        for move_line in move.move_line_ids:
                            sales_and_moves |= move_line
                return sales_and_moves
        elif not self._delivery_report_state_is_done():
            return moves
        else:
            return self._get_sorted_move_lines()

    def get_customer_refs(self):
        """Returns all unique sales order customer references."""
        if self._delivery_report_state_is_done():
            move_lines = self.move_lines
        else:
            move_lines = self.move_lines.filtered("product_uom_qty")
        references = move_lines.mapped("sale_line_id.order_id.client_order_ref")
        return set(filter(None, references))
