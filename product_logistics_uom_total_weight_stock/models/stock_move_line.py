# Copyright 2025 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    total_weight = fields.Float(compute="_compute_total_weight")

    @api.depends("quantity", "product_id.product_weight")
    def _compute_total_weight(self):
        for quant in self:
            quant.total_weight = (
                quant.quantity * quant.product_id.product_weight
            ) / quant.product_id.weight_uom_id.factor
