# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    product_apply_lot_restriction_domain = fields.Char(
        default="[]",
        help="Lot restriction during stock movements will only be "
        "applied to products in this domain.\n if empty, it applies "
        "to all products",
    )
