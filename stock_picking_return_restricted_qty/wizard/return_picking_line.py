# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            restrict_return_qty = (
                line.move_id.picking_id.picking_type_id.restrict_return_qty
            )

            qty = line.get_returned_restricted_quantity(line.move_id)

            if restrict_return_qty and line.quantity > qty:
                raise UserError(
                    self.env._("Return more quantities than delivered is not allowed.")
                )

    def get_returned_restricted_quantity(self, stock_move):
        """This function is created to know how many products
        have the person who tries to create a return picking
        on his hand."""
        qty = stock_move.product_qty
        for line in stock_move.move_dest_ids.move_line_ids:
            if (
                line.move_id.origin_returned_move_id
                and line.move_id.origin_returned_move_id != stock_move
            ):
                continue
            if line.state in {"partially_available", "assigned", "done"}:
                qty -= line.quantity
        return max(qty, 0.0)
