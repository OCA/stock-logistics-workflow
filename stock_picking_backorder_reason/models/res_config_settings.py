# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    partner_sale_backorder_default_strategy = fields.Selection(
        related="company_id.partner_sale_backorder_default_strategy",
        readonly=False,
    )
    partner_purchase_backorder_default_strategy = fields.Selection(
        related="company_id.partner_purchase_backorder_default_strategy", readonly=False
    )
