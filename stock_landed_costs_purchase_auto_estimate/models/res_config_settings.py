# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    estimated_landed_cost_product_id = fields.Many2one(
        related="company_id.estimated_landed_cost_product_id",
        readonly=False,
    )
