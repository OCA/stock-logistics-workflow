# -*- coding: utf-8 -*-
# ©2015 Agile Business Group (<http://www.agilebg.com>)
# ©2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


class TestStockMoveBackdating(common.TransactionCase):

    def setUp(self):
        super(TestStockMoveBackdating, self).setUp()

        self.demo_user = self.env.ref('base.user_demo')
        self.env.uid = self.demo_user.id
        self.move_model = self.env["stock.move"]
        self.picking_model = self.env["stock.picking"]
        self.product_model = self.env["product.product"]
        self.location_model = self.env["stock.location"]
        self.stock_transfer_details = self.env["stock.transfer_details"]

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
        pick = self.picking_out
        pick_wizard = self.stock_transfer_details.with_context(
            active_model='stock.picking',
            active_ids=[pick.id],
            active_id=len([pick.id]) and pick.id or False
        ).create(
            {'picking_id': pick.id}
        )
        pick_wizard.item_ids[0].write({'date': back_date})
        pick_wizard.do_detailed_transfer()

    def computeMove(self, timedelta_days):
        now = datetime.now()
        back_date = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        self.create_assigne_picking()
        self.run_picking(back_date)
        self.picking_out.action_done()
        move = self.move_id
        move.refresh()
        self.assertEqual(move.date[0:10], back_date)
        self.assertEqual(self.picking_out.state, 'done')
        self.assertEqual(move.state, 'done')
        for quant in move.quant_ids:
            self.assertEqual(quant.in_date[0:10], back_date)

    def test_0_stock_move_backdate_yesterday(self):
        self.computeMove(1)

    def test_1_stock_move_backdate_last_month(self):
        self.computeMove(31)

    def test_2_stock_move_backdate_future(self):
        self.assertRaises(
            orm.except_orm,
            self.computeMove, -1)
