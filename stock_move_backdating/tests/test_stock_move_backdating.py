# -*- coding: utf-8 -*-
# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning as UserError


class TestStockMoveBackdating(TransactionCase):

    def test_date_backdating_yesterday(self):
        date_backdating = self._get_date_backdating(1)
        self._transfer_picking_with_date(date_backdating)

    def test_date_backdating_last_month(self):
        date_backdating = self._get_date_backdating(31)
        self._transfer_picking_with_date(date_backdating)

    def test_date_backdating_future(self):
        date_backdating = self._get_date_backdating(-1)
        with self.assertRaises(UserError) as exc:
            self._transfer_picking_with_date(date_backdating)
        self.assertEqual(
            exc.exception.message,
            'You can not process an actual movement date in the future.')

    def test_different_dates_backdating(self):
        date_backdating_1 = self._get_date_backdating(1)
        date_backdating_2 = self._get_date_backdating(2)
        self._transfer_picking_with_dates(date_backdating_1, date_backdating_2)

    def _move_factory(self, product, qty):
        return self.env['stock.move'].create({
            'name': '/',
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })

    def _transfer_details_factory(self, picking):
        return self.env['stock.transfer_details'].with_context(
            active_model='stock.picking',
            active_ids=[picking.id],
            active_id=picking.id).create({'picking_id': picking.id})

    def _get_date_backdating(self, timedelta_days):
        now = datetime.now()
        date_backdating = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        return date_backdating

    def setUp(self):
        super(TestStockMoveBackdating, self).setUp()
        product_8 = self.env.ref('product.product_product_8')
        product_9 = self.env.ref('product.product_product_9')
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id})
        self.picking.move_lines = (
            self._move_factory(product=product_8, qty=1.0) |
            self._move_factory(product=product_9, qty=2.0))
        self.picking.action_confirm()
        self.picking.force_assign()

    def _transfer_picking_with_date(self, date_backdating):
        wizard = self._transfer_details_factory(self.picking)
        wizard.date_backdating = date_backdating
        wizard.onchange_date_backdating()
        self.assertEqual(wizard.item_ids[0].date[0:10], date_backdating)
        self.assertEqual(wizard.item_ids[0].date[0:10], date_backdating)
        wizard.do_detailed_transfer()
        self.assertEqual(self.picking.state, 'done')
        self.assertEqual(
            len(self.picking.move_lines), 2, 'Wrong number of move lines')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'done')
            self.assertEqual(move.date[0:10], date_backdating)
            for quant in move.quant_ids:
                self.assertEqual(quant.in_date[0:10], date_backdating)

        self.assertEqual(self.picking.date_done[0:10], date_backdating)

    def _transfer_picking_with_dates(
            self, date_backdating_1, date_backdating_2):
        wizard = self._transfer_details_factory(self.picking)
        wizard.item_ids[0].date = date_backdating_1
        wizard.item_ids[1].date = date_backdating_2
        wizard.item_ids[0].onchange_date()
        wizard.item_ids[1].onchange_date()
        wizard.do_detailed_transfer()
        self.assertEqual(self.picking.state, 'done')
        self.assertEqual(
            len(self.picking.move_lines), 2, 'Wrong number of move lines')
        move_1 = self.picking.move_lines[0]
        self.assertEqual(move_1.state, 'done')
        self.assertEqual(move_1.date[0:10], date_backdating_1)
        for quant in move_1.quant_ids:
            self.assertEqual(quant.in_date[0:10], date_backdating_1)
        move_2 = self.picking.move_lines[1]
        self.assertEqual(move_2.state, 'done')
        self.assertEqual(move_2.date[0:10], date_backdating_2)
        for quant in move_2.quant_ids:
            self.assertEqual(quant.in_date[0:10], date_backdating_2)

        max_date = max(date_backdating_1, date_backdating_2)
        self.assertEqual(self.picking.date_done[0:10], max_date)
