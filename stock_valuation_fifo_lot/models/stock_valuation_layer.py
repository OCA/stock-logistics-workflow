# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    lot_ids = fields.Many2many(
        comodel_name="stock.lot",
        string="Lots/Serials",
    )

    def _get_unconsumed_in_move_line(self, lot):
        self.ensure_one()
        return self.stock_move_id.move_line_ids.filtered(
            lambda x: x.lot_id == lot and x.qty_remaining
        )
