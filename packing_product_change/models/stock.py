# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume, Guewen Baconnier
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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class stock_move(models.Model):

    _inherit = "stock.move"

    old_product_id = fields.Many2one(
    'product.product', 'Ordered Product', readonly=True,
    help="The field will be fullfilled by the system with the "
         "customer ordered product when you choose to replace it "
         "during the packing operation.")

    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, readonly=True,
        domain=[('type', '<>', 'service')],
        states={'draft': [('readonly', False)]})

    def _prepare_replace_product_move(self, replace_by_product_id):
        product_obj=self.env['product.product']
        line_name = product_obj.browse(replace_by_product_id).name_get()[0][1]
        data = {'product_id': replace_by_product_id,
                'name': line_name}
        # Store the replaced product (only once to keep the product
        # ordered by the client if many replacements)
        if self.old_product_id:
            if self.old_product_id.id == replace_by_product_id:
                # selected the same product than the original
                data['old_product_id'] = False
        else:
            data['old_product_id'] = self.product_id.id
        return data

    @api.multi
    def replace_product(self, replace_by_product_id):
        for move in self:
            if move.state in ('done', 'cancel'):
                raise UserError('Error! You cannot replace a product'
                                ' on a delivered or canceled move!')
            data = self._prepare_replace_product_move(replace_by_product_id)
            self.write(data)
            if move.state == 'assigned':
                self.action_cancel()
                self.action_assign()
                # TODO check workflow
        return True

# from openerp.tools.translate import _
#
#     def replace_product(self, cr, uid, ids,
#                         replace_by_product_id, context=None):
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         for move in self.browse(cr, uid, ids, context=context):
#             if move.state in ('done', 'cancel'):
#                 raise orm.except_orm(
#                     _('Error!'),
#                     _("You cannot replace a product on a "
#                       "delivered or canceled move!"))
#
#             data = self._prepare_replace_product_move(
#                 cr, uid, move, replace_by_product_id, context=context)
#
#             # Make the replacement of the product.
#             self.write(cr, uid, [move.id], data, context=context)
#
#             # cancel the availability of the move
#             # and check it again
#             if move.state == 'assigned':
#                 self.cancel_assign(cr, uid, [move.id])
#                 self.action_assign(cr, uid, [move.id])
#         return True
#
#     def _prepare_replace_product_move(self, cr, uid, move,
#                                       replace_by_product_id, context=None):
#         if context is None:
#             context = {}
#         ctx = context.copy()
#         product_obj = self.pool['product.product']
#         if move.picking_id.partner_id:
#             partner_obj = self.pool['res.partner']
#             lang = partner_obj.browse(
#                 cr, uid, move.picking_id.partner_id.id).lang
#             ctx.update({'lang': lang})
#
#         line_name = product_obj.name_get(
#             cr, uid, [replace_by_product_id], context=ctx)[0][1]
#         data = {'product_id': replace_by_product_id,
#                 'name': line_name}
#
#         # Store the replaced product (only once to keep the product
#         # ordered by the client if many replacements)
#         if move.old_product_id:
#             if move.old_product_id.id == replace_by_product_id:
#                 # selected the same product than the original
#                 data['old_product_id'] = False
#         else:
#             data['old_product_id'] = move.product_id.id
#         return data


#????????????
# class stock_picking(models.Model):
#
#     _inherit = "stock.picking"  #??????????
#
#     BASE_TEXT_FOR_OLD_PRD_REPLACE = \
#         _("This product replaces partially or"
#           " completely the ordered product:")
#
#     def _prepare_invoice_line(self, picking, move_line,
#                               invoice_id, invoice_vals):
#         context = self._context or {}
#
#         vals = super(stock_picking, self)._prepare_invoice_line(
#             picking, move_line, invoice_id, invoice_vals)
#
#         if move_line.old_product_id:
#             partner_obj = self.env['res.partner']
#             prod_obj = self.env['product.product']
#             ctx = context.copy()
#             if move_line.picking_id.partner_id:
#                 lang = partner_obj.browse(move_line.picking_id.partner_id.id)
#                 ctx = {'lang': lang.lang}
#             product_note = prod_obj.name_get([move_line.old_product_id.id], context=ctx)[0][1]
#             vals['name'] = '\n'.join([vals['name'],self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
#                                                   product_note])

# class stock_picking(orm.Model):
#
#     _inherit = "stock.picking"
#
#     BASE_TEXT_FOR_OLD_PRD_REPLACE = \
#         _("This product replaces partially or"
#           " completely the ordered product:")
#
#     def _prepare_invoice_line(self, cr, uid, group, picking, move_line,
#                               invoice_id, invoice_vals, context=None):
#         """ Builds the dict containing the values for the invoice line
#
#             If a product has been replaced, add a note with the
#             replacement information
#
#             @param group: True or False
#             @param picking: picking object
#             @param: move_line: move_line object
#             @param: invoice_id: ID of the related invoice
#             @param: invoice_vals: dict used to created the invoice
#             @return: dict that will be used to create the invoice line
#         """
#         if context is None:
#             context = {}
#         vals = super(stock_picking, self)._prepare_invoice_line(
#             cr, uid, group, picking, move_line, invoice_id, invoice_vals,
#             context=context)
#
#         if move_line.old_product_id:
#             partner_obj = self.pool['res.partner']
#             prod_obj = self.pool['product.product']
#             ctx = context.copy()
#             if move_line.picking_id.partner_id:
#                 lang = partner_obj.browse(
#                     cr, uid, move_line.picking_id.partner_id.id)
#                 ctx = {'lang': lang.lang}
#
#             product_note = prod_obj.name_get(
#                 cr, uid, [move_line.old_product_id.id], context=ctx)[0][1]
#             vals['name'] = '\n'.join([vals['name'],
#                                       self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
#                                       product_note])
#
#         return vals
