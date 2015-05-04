# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'

    product_uos_qty = fields.Float(
        'Quantity (UOS)',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos = fields.Many2one(
        "product.uom", string='Product UOS', readonly=True)

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(StockTransferDetails, self).default_get(
            cr, uid, fields, context=context)
        if not res.get('item_ids') or len(res.get('item_ids')) != 1:
            return res

        for item in res.get('item_ids'):
            item.update(
                {
                    'product_uos': item.get('product_uom_id', False),
                    'product_uos_qty': item.get('quantity', 0)
                })
        if not res.get('packop_ids') or len(res.get('packop_ids')) != 1:
            return res

        for item in res.get('packop_ids'):
            item.update(
                {
                    'product_uos': item.get('product_uom_id', False),
                    'product_uos_qty': item.get('quantity', 0)
                })
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'
    _description = 'Picking wizard items'

    product_uos_qty = fields.Float(
        'Quantity (UOS)',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos = fields.Many2one(
        "product.uom", string='Product UOS', readonly=True)

    @api.onchange('product_uos_qty')
    def onchange_product_uos_qty(self):
        self.quantity = self.quantity * (self.product_uos_qty / self.quantity)
