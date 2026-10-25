# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    batch_group_by_date = fields.Boolean(
        string="Date",
        help="Automatically group batches by date.",
    )

    @api.model
    def _get_batch_group_by_keys(self):
        return super()._get_batch_group_by_keys() + ["batch_group_by_date"]
