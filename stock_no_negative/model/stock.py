# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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

from openerp import _, api, fields, exceptions, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        """
        Method to enable check unicity on quantity on hand

        We need this check after of process move to get
        real quantity after of this moves.
        TODO
        """
        for move in self.browse(cr, uid, ids, context=context):
            product = move.product_id
            location = move.location_id
            print product
            if product and product.check_no_negative and location and\
                    location.usage == 'internal':
                operations = self.get_operations_as_action_done(
                    cr, uid, ids, context=context)
                lot = False
                if operations:
                    lot = operations[0].lot_id
                if self.exist_ok(cr, uid, product, lot, location,
                                 context=context):
                    print 'rrrrrrr'
        print 'context', context
        res = super(StockMove, self).action_done(
            cr, uid, ids, context=context)
        return res

    def exist_ok(
            self, cr, uid, product_id=None, lot_id=None, location_id=None,
            context=None):
        stock_prod = self.pool.get('stock.quant')

        if lot_id:
            ctx = context.copy()
            ctx.update({'lot_id': lot_id.id})
            product_ctx = self.pool.get('product.product').browse(
                cr, uid, [product_id.id], context=ctx)[0]
            qty = product_ctx.qty_available
            #Revisar, porque la cantidad no es por ubicacion
        print 'qty', qty
        print '----------------'
        return True

