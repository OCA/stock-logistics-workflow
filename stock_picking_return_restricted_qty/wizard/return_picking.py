# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        val = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)
        return_lines = self.env["stock.return.picking.line"]
        val["quantity"] = return_lines.get_returned_restricted_quantity(stock_move)
        return val

    def _create_return(self):
        restrict_return_qty = self.picking_id.picking_type_id.restrict_return_qty

        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for return_line in self.product_return_moves:
            quantity = return_line.get_returned_restricted_quantity(return_line.move_id)

            if restrict_return_qty and (
                float_compare(
                    return_line.quantity, quantity, precision_digits=precision
                )
                > 0
            ):
                raise UserError(
                    self.env._("Return more quantities than delivered is not allowed.")
                )
        return super()._create_return()
