# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    location_ids = fields.Many2many(
        comodel_name="stock.location", compute="_compute_location_ids", store=True
    )

    @api.depends("quant_ids", "quant_ids.location_id")
    def _compute_location_ids(self):
        for lot in self:
            lot.location_ids = lot.quant_ids.filtered(lambda l: l.quantity > 0).mapped(
                "location_id"
            )
