# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    scrap_reason_required = fields.Boolean(
        config_parameter="scrap_order.scrap_reason_required",
    )
