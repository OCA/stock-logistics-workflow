# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_apply_lot_restriction_domain = fields.Char(
        related="company_id.product_apply_lot_restriction_domain",
        readonly=False,
    )
