# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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

from odoo import models, api
# from openerp.osv import orm


class stock_move(models.Model):
    _inherit = 'stock.move'

    def replace_equivalence(self):
        """ If a product with an equivalence is found on a
            move line, it is replaced by its equivalence."""
        for move in self:
            if move.picking_id and move.picking_id.picking_type_id.code == 'outgoing':
                if move.product_id.equivalent_id:
                    # replace_product is provided by the module
                    # packing_product_change
                    self.replace_product(move.id,
                                         move.product_id.equivalent_id.id)
        return True

    @api.model
    def create(self, vals):
        move_id = super(stock_move, self).create(vals)
        move_id.replace_equivalence()
        return move_id

    @api.multi
    def write(self, vals):
        res = super(stock_move, self).write(vals)
        self.replace_equivalence()
        return res

# class stock_move(orm.Model):
#     _inherit = 'stock.move'
#
#     def replace_equivalence(self, cr, uid, ids, context=None):
#         """ If a product with an equivalence is found on a
#             move line, it is replaced by its equivalence.
#         """
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         for move in self.browse(cr, uid, ids, context=context):
#             if move.picking_id and move.picking_id.type == 'out':
#                 if move.product_id.equivalent_id:
#                     # replace_product is provided by the module
#                     # packing_product_change
#                     self.replace_product(
#                         cr, uid,
#                         move.id,
#                         move.product_id.equivalent_id.id,
#                         context=context)
#         return True
#
#     def create(self, cr, uid, vals, context=None):
#         move_id = super(stock_move, self).create(cr, uid, vals, context=context)
#         self.replace_equivalence(cr, uid, move_id, context=context)
#         return move_id
#
#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
#         self.replace_equivalence(cr, uid, ids, context=context)
#         return res
