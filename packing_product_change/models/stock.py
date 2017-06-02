# -*- coding: utf-8 -*-
# Copyright 2010-2012, 2017 Camptocamp
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
            data = move._prepare_replace_product_move(replace_by_product_id)
            move.write(data)
            if move.state == 'assigned':
                move.action_cancel()
                move.action_assign()
                # TODO check workflow
        return True
