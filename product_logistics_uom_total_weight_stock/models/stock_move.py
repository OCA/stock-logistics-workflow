# Copyright 2025 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    total_weight = fields.Float(
        compute="_compute_total_weight",
        store=True,
    )

    @api.depends("product_id.product_weight", "quantity")
    def _compute_total_weight(self):
        for record in self:
            record.total_weight = record.product_id.product_weight * record.quantity
