from collections import namedtuple
from itertools import groupby

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sale_ids = fields.Many2many("sale.order", compute="_compute_sale_ids", store=True)
    # don't copy the printed state of a picking otherwise the backorder of a
    # printed picking becomes printed
    printed = fields.Boolean(copy=False)

    @api.depends("move_lines.group_id.sale_id")
    def _compute_sale_ids(self):
        for rec in self:
            rec.sale_ids = rec.mapped("move_lines.group_id.sale_id")

    def write(self, values):
        if self.env.context.get("picking_no_overwrite_partner_origin"):
            written_fields = set(values.keys())
            if written_fields == {"partner_id", "origin"}:
                values = {}
        return super().write(values)

    def action_cancel(self):
        cancel_sale_id = self.env.context.get("cancel_sale_id")
        if cancel_sale_id:
            moves = self.mapped("move_lines").filtered(
                lambda m: m.group_id.sale_id.id == cancel_sale_id
                and m.state not in ("done", "cancel")
            )
            moves.with_context(cancel_sale_id=False)._action_cancel()
            return True
        else:
            return super().action_cancel()

    def _create_backorder(self):
        return super(
            StockPicking, self.with_context(picking_no_copy_if_can_group=1)
        )._create_backorder()

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

    def do_something(self):
        return "bla bla"

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
                            description_picking=sale.name,
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
                            description_picking=sale.name,
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


MockedMove = namedtuple(
    "MockedMove",
    ["product_id", "description_picking", "product_uom_qty", "product_uom", "lot_name"],
)
