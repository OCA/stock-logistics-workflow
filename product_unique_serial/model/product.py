# -*- coding: utf-8 -*-
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lot_unique_ok = fields.Boolean('Unique lot',
                                   help='Forces set qty=1 '
                                        'to specify a Unique '
                                        'Serial Number for '
                                        'all moves')
