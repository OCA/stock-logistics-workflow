# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import users

from .common import TestStockCustomerDepositCommon


class TestSaleCustomerDeposits(TestStockCustomerDepositCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        stock_dict = {
            cls.productA: {False: 300},
            cls.productB: {False: 300},
        }
        cls.update_availiable_quantity(cls, stock_dict)
        cls.result_test = {
            False: {
                cls.productA: 200,
                cls.productB: 190,
            },
            cls.partner1: {
                cls.productA: 100,
                cls.productB: 110,
            },
        }

    @users("user_customer_deposit")
    def test_sale_customer_deposit(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1_child
        so_form.warehouse_id = self.warehouse
        so_form.customer_deposit = True
        with so_form.order_line.new() as line:
            line.product_id = self.productA
            line.product_uom_qty = 100.0
        with so_form.order_line.new() as line:
            line.product_id = self.productB
            line.product_uom_qty = 110.0
        so = so_form.save()
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
            ],
        )
        so.action_confirm()
        self.assertEqual(so.invoice_status, "to invoice")
        self.assertEqual(len(so.picking_ids), 1)
        self.assertRecordValues(
            so.picking_ids,
            [
                {
                    "picking_type_id": self.warehouse.customer_deposit_type_id.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                }
            ],
        )
        self.assertRecordValues(
            so.picking_ids.move_ids,
            [
                {
                    "picking_type_id": self.warehouse.customer_deposit_type_id.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                },
                {
                    "picking_type_id": self.warehouse.customer_deposit_type_id.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                },
            ],
        )
        self.assertRecordValues(
            so.picking_ids.move_line_ids,
            [
                {
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                },
                {
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                },
            ],
        )
        so.picking_ids.action_confirm()
        so.picking_ids.action_assign()
        so.picking_ids.action_set_quantities_to_reservation()
        so.picking_ids.button_validate()
        # Check valuation layers has been created when creating a deposit
        self.assertTrue(so.picking_ids.move_ids.stock_valuation_layer_ids)
        for partner, products in self.result_test.items():
            for product, quantity in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    quantity,
                )

    @users("user_customer_deposit")
    def test_sale_customer_deposit_wrong_route(self):
        """Confirm sale order with wrong configuration."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1_child
        so_form.warehouse_id = self.warehouse
        so_form.customer_deposit = True
        with so_form.order_line.new() as line:
            line.product_id = self.productA
            line.product_uom_qty = 100.0
        with so_form.order_line.new() as line:
            line.product_id = self.productB
            line.product_uom_qty = 110.0
        so = so_form.save()
        so.order_line[0].route_id = False
        with self.assertRaises(
            ValidationError,
            msg="All lines coming from orders marked as 'Customer depot' "
            "must have Customer deposit route.",
        ):
            so.action_confirm()
        so.customer_deposit = False
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": False,
                },
                {
                    "route_id": False,
                },
            ],
        )
        so.order_line.route_id = self.warehouse.customer_deposit_route_id
        with self.assertRaises(
            ValidationError,
            msg="You cannot select Customer Deposit route in an order line "
            "if you do not mark the order as a customer depot.",
        ):
            so.action_confirm()
