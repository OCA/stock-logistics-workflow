# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    enforce_lot_restriction_product_domain = fields.Char(
        default="[]",
        string="Enforce lot restrictions",
        help="Lot restriction of stock movements cannot be changed "
        "for products in this domain.\n if empty, lot restrictions "
        "cannot be changed for any product.",
    )
