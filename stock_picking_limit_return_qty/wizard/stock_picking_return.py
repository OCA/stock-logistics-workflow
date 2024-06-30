# Copyright 2024 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):

        res = super(
            ReturnPicking, self
        )._prepare_stock_return_picking_line_vals_from_move(stock_move)

        # Store maximum quantity that is possible to return
        res.update(
            {
                "quantity_max": res["quantity"],
            }
        )
        return res
