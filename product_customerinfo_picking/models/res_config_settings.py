# Copyright 2026 Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    display_customer_product_info_report = fields.Boolean(
        related="company_id.display_customer_product_info_report",
        readonly=False,
    )
