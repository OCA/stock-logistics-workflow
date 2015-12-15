# -*- coding: utf-8 -*-
##############################################################################
#
#    Product serial module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, api
from openerp.tools import float_compare


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        ppo = self.env['product.product']
        new_items = []
        for item in res['item_ids']:
            product = ppo.browse(item['product_id'])
            if product.lot_split_type == 'single' and item['quantity'] > 1:
                qty = item['quantity']
                item['quantity'] = 1
                new_items.append(item)  # put first item linked to packop_id
                qty -= 1
                final_item = item.copy()
                # next items are not linked to a packop_id
                final_item['packop_id'] = False
                while float_compare(qty, 1.0, precision) == 1:
                    new_items.append(final_item.copy())
                    qty -= 1
                final_item['quantity'] = qty
                new_items.append(final_item)
            else:
                new_items.append(item)
        res.update(item_ids=new_items)
        return res
