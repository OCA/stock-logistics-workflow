# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        vals = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)
        vals["description"] = stock_move.description_picking
        return vals


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    description = fields.Text()

    def _prepare_move_default_values(self, new_picking):
        vals = super()._prepare_move_default_values(new_picking)
        vals["description_picking"] = self.description
        return vals
