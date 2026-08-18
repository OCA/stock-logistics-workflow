# Copyright 2026 Giuseppe Borruso (gborruso@dinamicheaziendali.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompanyInherit(models.Model):
    _inherit = "res.company"

    display_customer_product_info_report = fields.Boolean(
        "Display Customer Product Info in Picking Report",
        default=False,
    )
