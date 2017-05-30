# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
# from openerp.osv import orm, fields


class Product(models.Model):
    _inherit = 'product.product'
    equivalent_id = fields.Many2one('product.product', 'Equivalent Product')
    compatibility_ids = fields.Many2many(
        'product.product', 'product_compatibility_rel', 'product_id',
        'compatible_id', string='Compatibility')
