# -*- coding: utf-8 -*-
# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError


class TestStockMoveBackdating(TransactionCase):

    def test_date_backdating_yesterday(self):
        date_backdating = self._get_date_backdating(1)
        self._transfer_picking_with_date(date_backdating)

    def test_date_backdating_last_month(self):
        date_backdating = self._get_date_backdating(31)
        self._transfer_picking_with_date(date_backdating)

    def test_date_backdating_future(self):
        date_backdating = self._get_date_backdating(-1)
        with self.assertRaises(UserError):
            self._transfer_picking_with_date(date_backdating)

    def test_different_dates_backdating(self):
        date_backdating_1 = self._get_date_backdating(1)
        date_backdating_2 = self._get_date_backdating(2)
        self._transfer_picking_with_dates(date_backdating_1, date_backdating_2)

    def _move_factory(self, name, product, qty):
        return self.env['stock.move'].create({
            'name': name,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })

    def _get_date_backdating(self, timedelta_days):
        now = datetime.now()
        date_backdating = (now - timedelta(days=timedelta_days)).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        return date_backdating

    def _get_corresponding_pack_operation(self, move):
        return move.linked_move_operation_ids.operation_id

    def setUp(self):
        super(TestStockMoveBackdating, self).setUp()
        product_8 = self.env.ref('product.product_product_8')
        product_9 = self.env.ref('product.product_product_9')
        # enable perpetual valuation
        product_8.valuation = 'real_time'
        product_9.valuation = 'real_time'
        picking_type = self.env.ref('stock.picking_type_out')
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id})
        self.picking.move_lines = (
            self._move_factory(name='move_1', product=product_8, qty=1.0) |
            self._move_factory(name='move_2', product=product_9, qty=2.0))
        self.picking.action_confirm()
        self.picking.force_assign()
        self.pack_operations = self.picking.pack_operation_product_ids
        self.assertEqual(len(self.pack_operations), 2)

    def _check_account_moves(self, account_moves):
        # check numbers of account moves created by perpetual valuation
        # it has to be equal to the number of stock moves
        self.assertEqual(len(account_moves), len(self.picking.move_lines))

    def _check_account_move_date(self, account_move, date):
        self.assertEqual(account_move.date[0:10], date[0:10])

    def _search_account_move(self, picking, move):
        account_move = self.env['account.move'].search(
            [('ref', '=', picking.name),
             ('line_ids.name', '=', move.name)])
        return account_move

    def _transfer_picking_with_date(self, date_backdating):
        self.pack_operations[0].date_backdating = date_backdating
        self.pack_operations[1].date_backdating = date_backdating
        self.picking.do_transfer()
        account_moves = self.env['account.move'].search(
            [('ref', '=', self.picking.name)])
        self._check_account_moves(account_moves)
        self.assertEqual(self.picking.state, 'done')
        self.assertEqual(
            len(self.picking.move_lines), 2, 'Wrong number of move lines')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'done')
            self.assertEqual(move.date[0:10], date_backdating)
            for quant in move.quant_ids:
                self.assertEqual(quant.in_date[0:10], date_backdating)

        self.assertEqual(self.picking.date_done[0:10], date_backdating)
        for account_move in account_moves:
            self._check_account_move_date(account_move, date_backdating)

    def _transfer_picking_with_dates(
            self, date_backdating_1, date_backdating_2):
        self.pack_operations[0].date_backdating = date_backdating_1
        self.pack_operations[1].date_backdating = date_backdating_2
        self.picking.do_transfer()
        account_moves = self.env['account.move'].search(
            [('ref', '=', self.picking.name)])
        self._check_account_moves(account_moves)
        self.assertEqual(self.picking.state, 'done')
        self.assertEqual(
            len(self.picking.move_lines), 2, 'Wrong number of move lines')
        move_1 = self.picking.move_lines[0]
        pack_op_1 = self._get_corresponding_pack_operation(move_1)
        self.assertEqual(move_1.state, 'done')
        self.assertEqual(move_1.date[0:10], pack_op_1.date_backdating[0:10])
        for quant in move_1.quant_ids:
            self.assertEqual(
                quant.in_date[0:10], pack_op_1.date_backdating[0:10])
        move_2 = self.picking.move_lines[1]
        pack_op_2 = self._get_corresponding_pack_operation(move_2)
        self.assertEqual(move_2.state, 'done')
        self.assertEqual(move_2.date[0:10], pack_op_2.date_backdating[0:10])
        for quant in move_2.quant_ids:
            self.assertEqual(
                quant.in_date[0:10], pack_op_2.date_backdating[0:10])

        max_date = max(date_backdating_1, date_backdating_2)
        self.assertEqual(self.picking.date_done[0:10], max_date)
        account_move_1 = self._search_account_move(self.picking, move_1)
        account_move_2 = self._search_account_move(self.picking, move_2)
        self._check_account_move_date(account_move_1, move_1.date)
        self._check_account_move_date(account_move_2, move_2.date)
