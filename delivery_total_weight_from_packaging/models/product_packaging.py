# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    base_weight = fields.Float(string='Base Weight', help='Weight of the packaging')
