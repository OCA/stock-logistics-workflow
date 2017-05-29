# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2010 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields
# from openerp.osv import orm, fields

class Product(models.Model):
    _inherit = 'product.product'
    equivalent_id = fields.Many2one('product.product','Equivalent Product')
    compatibility_ids = fields.Many2many('product.product',
                        'product_compatibility_rel','product_id',
                        'compatible_id', string='Compatibility')

# class Product(orm.Model):
#     """ Inherit product in order to manage equivalences"""
#     _inherit = 'product.product'
#
#     _columns = {
#         'equivalent_id': fields.many2one(
#             'product.product', 'Equivalent Product'),
#         'compatibility_ids': fields.many2many(
#             'product.product',
#             'product_compatibility_rel',
#             'product_id',
#             'compatible_id',
#             string='Compatibility'
#         ),
#     }
