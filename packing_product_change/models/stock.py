# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):

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
        product = self.env['product.product']
        line_name = product.browse(replace_by_product_id).name_get()[0][1]
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
                raise UserError(_('Error! You cannot replace a product'
                                ' on a delivered or canceled move!'))
            data = self._prepare_replace_product_move(replace_by_product_id)
            self.write(data)
            if move.state == 'assigned':
                self.action_cancel()
                self.action_assign()
                # TODO check workflow
        return True

# ???????????? ported this method but was unable to find similar
# method in stock.picking
# class StockPicking(models.Model):
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
#                 lang = partner_obj.browse(
#                       move_line.picking_id.partner_id.id)
#                 ctx = {'lang': lang.lang}
#             product_note = prod_obj.name_get(
#                     [move_line.old_product_id.id], context=ctx)[0][1]
#             vals['name'] = '\n'.join([
#                         vals['name'],self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
#                                                   product_note])
