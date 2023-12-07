# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enforce_lot_restriction_product_domain = fields.Char(
        related="company_id.enforce_lot_restriction_product_domain",
        readonly=False,
    )
