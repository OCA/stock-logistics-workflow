# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lot_default_locked = fields.Boolean(
        string='Block new Serial Numbers/lots',
        help='If checked, future Serial Numbers/lots will be created blocked by default')
