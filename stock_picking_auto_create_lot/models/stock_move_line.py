# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_lot_sequence(self):
        self.ensure_one()
        return self.env["ir.sequence"].next_by_code("stock.lot.serial")
