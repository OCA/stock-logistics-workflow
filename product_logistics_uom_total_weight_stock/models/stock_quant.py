# Copyright 2025 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_weight = fields.Float("Total Weight", compute="_compute_inventory_weight")

    @api.depends("quantity", "product_id.product_weight")
    def _compute_inventory_weight(self):
        for quant in self:
            quant.inventory_weight = (
                quant.quantity * quant.product_id.product_weight
            ) / quant.product_id.weight_uom_id.factor
