# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

CONFIG_PARAM_SKU_TRAILING = "stock_picking_auto_create_lot.sku_based_numbers_trailing"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sku_based_numbers_trailing = fields.Integer(
        default=0,
        config_parameter=CONFIG_PARAM_SKU_TRAILING,
        help="Number of leading zeroes for SKU-based lot/serial suffix (e.g. 3 -> 001)",
    )

    @api.constrains("sku_based_numbers_trailing")
    def _check_sku_based_numbers_trailing(self):
        for rec in self:
            if rec.sku_based_numbers_trailing < 0:
                raise ValidationError(
                    self.env._("SKU Based Numbers Trailing must be 0 or greater.")
                )
