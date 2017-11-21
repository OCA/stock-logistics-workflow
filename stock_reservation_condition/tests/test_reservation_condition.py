# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
from odoo.tests.common import TransactionCase


class TestReservationCondition(TransactionCase):

    def setUp(self):
        super(TestReservationCondition, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.purchase_order_model = self.env['purchase.order']
        self.stock_move_model = self.env['stock.move']
        self.product_model = self.env['product.product']

        self.customer = self.env['res.partner'].create({
            'name': 'Customer',
            'email': 'customer@komit',
            'supplier': False,
            'customer': True,
            'is_company': False,
        })
        self.vendor = self.env['res.partner'].create({
            'name': 'Vendor',
            'email': 'vendor@komit',
            'supplier': True,
            'customer': False,
            'is_company': False,
        })
        self.product_a = self.product_model.create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'uom_po_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PRODUCT-A',
            'sale_ok': True,
            'purchase_ok': True,
        })

        self.product_b = self.product_model.create({
            'name': 'Product B',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'uom_po_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PRODUCT-B',
            'sale_ok': True,
            'purchase_ok': True,
        })

        # Update stock
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_a.id,
            'new_quantity': 20.0,
            'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id,
        })
        inventory_wizard.change_product_qty()

    def _check_move_state(self, move, state):
        self.assertEqual(
            move.state,
            state,
            "System don't skip reservation when user confirm SO")

    def _check_picking_state(self, picking, state):
        self.assertEqual(
            picking.state,
            state,
            "System don't skip reservation when user confirm SO")

    def _test_skip_reservation(self, order, expected_stock_state):
        for picking in order.picking_ids:
            self.assertEqual(picking.state, expected_stock_state)
            for move in picking.move_lines:
                self.assertEqual(move.state, expected_stock_state)

    def create_sale_order(self, reservation_date=False, purchase_id=False):
        vals = {
            'partner_id': self.customer.id,
            'partner_invoice_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'reservation_date': reservation_date,
            'order_line': [(0, 0, {
                'name': self.product_a.name,
                'product_id': self.product_a.id,
                'product_uom_qty': 5,
                'product_uom': self.product_a.uom_id.id,
                'price_unit': self.product_a.list_price
            })],
            'pricelist_id': self.env.ref('product.list0').id
        }
        if purchase_id:
            vals['reservation_po_ids'] = [(6, 0, [purchase_id])]
        sale_order = self.sale_order_model.create(vals)
        sale_order.action_confirm()
        return sale_order

    def purchase_product(self, product_id, reservation_date=False):
        product = self.product_model.browse(product_id)
        purchase_order = self.purchase_order_model.create({
            'partner_id': self.vendor.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_qty': 2.0,
                    'product_uom': product.uom_po_id.id,
                    'date_planned': datetime.today(),
                    'price_unit': 1,
                })],
        })
        purchase_order.button_confirm()
        purchase_order.picking_ids.write({'min_date': reservation_date})
        purchase_order._compute_reservation_date()
        return purchase_order

    def test_case_1(self):
        # Case 1: SO with no Reservation Date and Purchase order
        sale_order = self.create_sale_order()
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='assigned')
        logging.info("Case 1 pass")

    def test_case_2(self):
        # Case 2: SO with Reservation Date in tomorrow
        sale_order = self.create_sale_order(
            reservation_date=date.today() + relativedelta(days=1))
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='confirmed')
        logging.info("Case 2 pass")

    def test_case_3(self):
        # Case 3: SO with Reservation Date is yesterday
        sale_order = self.create_sale_order(
            reservation_date=date.today() - relativedelta(days=1))
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='assigned')
        logging.info("Case 3 pass")

    def test_case_4(self):
        # Case 4: SO and Related PO with Reservation Date in tomorrow
        purchase_order = self.purchase_product(
            product_id=self.product_a.id,
            reservation_date=date.today() + relativedelta(days=1))
        sale_order = self.create_sale_order(purchase_id=purchase_order.id)
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='confirmed')
        logging.info("Case 4 pass")

    def test_case_5(self):
        # Case 5: SO and Related PO with Reservation Date in yesterday
        purchase_order = self.purchase_product(
            product_id=self.product_a.id,
            reservation_date=date.today() - relativedelta(days=1))
        sale_order = self.create_sale_order(purchase_id=purchase_order.id)
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='assigned')
        logging.info("Case 5 pass")

    def test_case_6(self):
        # Case 6: SO and Related PO with Reservation Date in tomorrow
        # but no line in Pikcing of PO contains any product in SO Line
        purchase_order = self.purchase_product(
            product_id=self.product_b.id,
            reservation_date=date.today() + relativedelta(days=1))
        sale_order = self.create_sale_order(purchase_id=purchase_order.id)
        self._test_skip_reservation(
            order=sale_order, expected_stock_state='assigned')
        logging.info("Case 6 pass")
