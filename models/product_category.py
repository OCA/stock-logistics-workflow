# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lot_default_locked = fields.Boolean(
        string='Create lot in locked status',
        help='If checked, production lots will be created locked by default')
