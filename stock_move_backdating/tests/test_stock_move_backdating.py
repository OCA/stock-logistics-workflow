# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#    Copyright (C) 2015 Agile Business Group  (<http://www.agilebg.com>)
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


class TestStockMoveBackdating(common.TransactionCase):

    def getDemoObject(self, module, data_id):
        if module == '':
            module = 'stock_move_backdating'
        xmlid = '%s.%s' % (module, data_id)
        return self.model_data.xmlid_to_object(xmlid)

    def getIdDemoObj(self, module, data_id):
        return self.getDemoObject(module, data_id).id

    def setUp(self):
        super(TestStockMoveBackdating, self).setUp()

        self.user_model = self.env["res.users"]
        self.move_model = self.env["stock.move"]
        self.product_model = self.env["product.product"]
        self.location_model = self.env["stock.location"]
        self.model_data = self.env['ir.model.data']

        product_uom_id = self.env['product.uom'].search([])[0]

        product_id = self.product_model.create(
            {
                'name': 'Prod 1',
                'uom_id': product_uom_id.id,
                'uom_po_id': product_uom_id.id,
                'standard': 'standard',
            }
        )
        product_id.product_tmpl_id.write(
            {
                'property_stock_account_input': (
                    self.getIdDemoObj('account','income_fx_income')
                ),
                'property_stock_account_output': (
                    self.getIdDemoObj('account','a_expense')
                )
            }
        )
        location_id = self.location_model.search(
            [('usage', '=', 'internal')])[0]

        location_supplier_id = self.location_model.search(
            [('usage', '=', 'supplier')])[0]

        self.move_id = self.move_model.create(
            {
                'product_id': product_id.id,
                'product_uom_qty': 10,
                'name': 'Test',
                'location_id': location_id.id,
                'location_dest_id': location_supplier_id.id,
                'product_uom': product_uom_id.id,
            })
        self.move_id.refresh()

    def ComputeMove(self, timedelta_days):

        move = self.move_id

        now = datetime.now()

        back_date = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)

        move.write({'date_backdating': back_date})
        move.action_done()
        move.refresh()

        self.assertEqual(move.date[0:10], back_date)

    def test_0_stock_move_backdate_yesterday(self):
        self.ComputeMove(1)

    def test_1_stock_move_backdate_last_month(self):
        self.ComputeMove(31)

    def test_2_stock_move_backdate_future(self):
        self.assertRaises(
            orm.except_orm,
            self.ComputeMove, -1)
