# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    threshold_filter_cost_min = fields.Monetary(
        related="company_id.threshold_filter_cost_min",
        readonly=False,
    )
    threshold_filter_qty_diff_min = fields.Float(
        related="company_id.threshold_filter_qty_diff_min",
        readonly=False,
    )
