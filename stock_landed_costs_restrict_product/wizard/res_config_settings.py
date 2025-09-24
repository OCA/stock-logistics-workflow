# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    landed_costs_apply_rule = fields.Boolean(
        "Apply landed cost rules",
        default=False,
        config_parameter="stock_landed_costs_product.landed_costs_apply_rule",
    )
