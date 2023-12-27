# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_note = fields.Text()

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.sale_note:
            res["sale_note"] = self.sale_note
        return res
