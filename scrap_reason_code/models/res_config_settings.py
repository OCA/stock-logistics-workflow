# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    scrap_reason_code_required = fields.Boolean(
        config_parameter="scrap_order.scrap_reason_code_required",
    )
