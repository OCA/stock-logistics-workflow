# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    vendor_comment = fields.Char()

    def _compute_display_name(self):
        res = super()._compute_display_name()
        for move in self:
            if move.vendor_comment:
                move.display_name = f"{move.display_name} {move.vendor_comment}"
        return res
