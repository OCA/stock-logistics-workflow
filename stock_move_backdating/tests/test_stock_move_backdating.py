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

    def setUp(self):
        super(TestStockMoveBackdating, self).setUp()

        self.user_model = self.env["res.users"]
        self.move_model = self.env["stock.move"]
        self.product_model = self.env["product.product"]
        self.location_model = self.env["stock.location"]
        self.model_data = self.env['ir.model.data']
        self.stock_transfer_details = self.registry("stock.transfer_details")

        self.product_uom_id = self.env['product.uom'].search([])[0]

        self.location_id = self.location_model.search(
            [('usage', '=', 'internal')])[0]

        self.location_supplier_id = self.location_model.search(
            [('usage', '=', 'supplier')])[0]

        self.product_id = self.product_model.create(
            {
                'name': 'Prod 1',
                'uom_id': self.product_uom_id.id,
                'uom_po_id': self.product_uom_id.id,
            }
        )
        self.product_id.product_tmpl_id.write(
            {
                'property_stock_account_input': (
                    self.ref('account.income_fx_income')
                ),
                'property_stock_account_output': (
                    self.ref('account.a_expense')
                )
            }
        )

    def create_assigne_picking(self):
        self.picking_out = self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out')})

        self.move_id = self.move_model.create(
            {
                'product_id': self.product_id.id,
                'product_uom_qty': 10,
                'name': 'Test',
                'location_id': self.location_id.id,
                'location_dest_id': self.location_supplier_id.id,
                'product_uom': self.product_uom_id.id,
                'picking_id': self.picking_out.id
            })

        self.picking_out.action_confirm()
        self.picking_out.force_assign()

    def run_picking(self, back_date):
        cr = self.env.cr
        uid = self.env.uid
        pick = self.picking_out
        context = self.env.context.copy()
        context.update(
            {
                'active_model': 'stock.picking',
                'active_ids': [pick.id],
                'active_id': len([pick.id]) and pick.id or False
            }
        )
        pick_wizard_id = self.stock_transfer_details.create(
            cr, uid, {'picking_id': pick.id}, context)
        pick_wizard = self.stock_transfer_details.browse(
            cr, uid, pick_wizard_id)
        pick_wizard.item_ids[0].write({'date': back_date})
        return self.stock_transfer_details.do_detailed_transfer(
            cr, uid, [pick_wizard_id], context)

    def ComputeMove(self, timedelta_days):
        now = datetime.now()
        back_date = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        self.create_assigne_picking()
        self.run_picking(back_date)
        self.picking_out.action_done()
        move = self.move_id
        move.refresh()
        self.assertEqual(move.date[0:10], back_date)
        for quant in move.quant_ids:
            self.assertEqual(quant.in_date[0:10], back_date)

    def test_0_stock_move_backdate_yesterday(self):
        self.ComputeMove(1)

    def test_1_stock_move_backdate_last_month(self):
        self.ComputeMove(31)

    def test_2_stock_move_backdate_future(self):
        self.assertRaises(
            orm.except_orm,
            self.ComputeMove, -1)
