# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm
from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


class test_stock_move_backdating(common.TransactionCase):
    def setUp(self):
        super(test_stock_move_backdating, self).setUp()

        self.user_model = self.registry("res.users")
        self.move_model = self.registry("stock.move")
        self.product_model = self.registry("product.product")
        self.location_model = self.registry("stock.location")
        self.user_model = self.registry("res.users")
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context

        product_id = self.product_model.create(
            cr, uid, {'name': 'Prod 1'}, context=context)

        location_id = self.location_model.search(
            cr, uid, [('usage', '=', 'internal')], context=context)[0]

        location_supplier_id = self.location_model.search(
            cr, uid, [('usage', '=', 'supplier')], context=context)[0]

        product_uom_id = self.registry('product.uom').search(
            cr, uid, [], context=context)[0]

        self.move_id = self.move_model.create(
            cr, uid, {
                'product_id': product_id,
                'product_qty': 10,
                'name': 'Test',
                'location_id': location_id,
                'location_dest_id': location_supplier_id,
                'product_uom': product_uom_id,
            }, context=context)

    def compute_move(self, timedelta_days):
        cr, uid, context = self.cr, self.uid, self.context
        move = self.move_model.browse(
            cr, uid, self.move_id, context=context)

        now = datetime.now()

        back_date = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

        move.write({'date_backdating': back_date})
        move.action_done()
        move.refresh()

        self.assertEqual(move.date[0:10], back_date)

    def test_stock_move_backdate_yesterday(self):
        self.compute_move(1)

    def test_stock_move_backdate_last_month(self):
        self.compute_move(31)

    def test_stock_move_backdate_future(self):
        self.assertRaises(
            orm.except_orm,
            self.compute_move, -1)
