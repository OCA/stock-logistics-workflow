# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
