# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    auto_create_lot = fields.Boolean(
        string='Auto create lot',
    )
