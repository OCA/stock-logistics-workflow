# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    partner_sale_backorder_default_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        default="create",
        required=True,
        help="Choose the default strategy to set on partners for backorders "
        "on sale flows (for customers).",
    )
    partner_purchase_backorder_default_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        default="create",
        required=True,
        help="Choose the default strategy to set on partners for backorders "
        "on purchase flows (for suppliers).",
    )
