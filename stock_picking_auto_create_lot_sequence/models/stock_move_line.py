# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_lot_sequence(self):
        self.ensure_one()
        if not self.product_id.lot_sequence_id:
            return super()._get_lot_sequence()
        seq_policy = self.env["stock.lot"]._get_sequence_policy()
        if seq_policy != "product":
            return super()._get_lot_sequence()
        return self.product_id.lot_sequence_id._next()
