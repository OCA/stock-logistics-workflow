# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2010-2012 Camptocamp SA
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

class replace_product(models.TransientModel):

    _name = "replace.product"
    _description = "Replace Product"

    product_id = fields.Many2one('product.product',
                                 'Replace by product',
                                 required=True,
                                 help="Choose which product will replace the original one.")

    def replace(self):
        rec_id = self.env.context.get('active_id')
        replacement_product = self.product_id
        move = self.env['stock.move'].browse(rec_id)
        move.replace_product(replacement_product.id)
        return{'type': 'ir.actions.act_window_close'}

# class replace_product(orm.TransientModel):
#
#     _name = "replace.product"
#     _description = "Replace Product"
#
#     _columns = {
#         'product_id': fields.many2one(
#             'product.product',
#             'Replace by product',
#             required=True,
#             help="Choose which product will replace the original one."),
#     }
#
#     def replace(self, cr, uid, ids, context=None):
#         context = context or {}
#         rec_id = context.get('active_id')
#
#         replacement_product = self.browse(
#             cr, uid, ids[0], context=context).product_id
#         self.pool.get('stock.move').replace_product(
#             cr, uid, rec_id, replacement_product.id, context=context)
#         return {'type': 'ir.actions.act_window_close'}
