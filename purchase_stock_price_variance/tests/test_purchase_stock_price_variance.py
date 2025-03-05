# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseStockPriceVariance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.user.company_id
        cls.product_category = cls.env["product.category"].create(
            {"name": "Test Category"}
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "standard_price": 100,
                "categ_id": cls.product_category.id,
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Test Supplier"})
        cls.group_manage_price_variance_check = cls.env.ref(
            "purchase_stock_price_variance.group_manage_price_variance_check"
        )
        cls.company.enable_price_variance_error = True

    def create_purchase_order(self, price_unit=100):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.product_variant_id.id,
                            "product_qty": 1,
                            "price_unit": price_unit,
                        }
                    )
                ],
            }
        )

    def validate_picking(self, picking, expect_error=False):
        picking.move_ids.write({"quantity_done": 1})
        if expect_error:
            with self.assertRaises(UserError):
                picking.button_validate()
        else:
            picking.button_validate()
            self.assertEqual(picking.state, "done")

    def check_chatter_message(self, picking, should_contain):
        messages = picking.message_ids.mapped("body")
        found = any(
            "Price variance exceeding a threshold detected" in message
            for message in messages
        )
        self.assertEqual(found, should_contain)

    def test_01_normal_workflow_no_error(self):
        po = self.create_purchase_order()
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking)
        self.check_chatter_message(picking, False)

    def test_02_price_variance_check_category(self):
        with self.assertRaises(UserError):
            self.product_category.bypass_price_variance_check = True
        self.product.price_variance_threshold_percent = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking, expect_error=True)
        self.env.user.groups_id |= self.group_manage_price_variance_check
        self.product_category.bypass_price_variance_check = True
        self.validate_picking(picking)
        self.check_chatter_message(picking, True)

    def test_03_price_variance_check_product(self):
        with self.assertRaises(UserError):
            self.product.bypass_price_variance_check = True
        self.product.price_variance_threshold_percent = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking, expect_error=True)
        self.env.user.groups_id |= self.group_manage_price_variance_check
        self.product.bypass_price_variance_check = True
        self.validate_picking(picking)
        self.check_chatter_message(picking, True)

    def test_04_price_variance_check_threshold_amount(self):
        self.product.price_variance_threshold_amount = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking, expect_error=True)
        self.env.user.groups_id |= self.group_manage_price_variance_check
        self.product.bypass_price_variance_check = True
        self.validate_picking(picking)
        self.check_chatter_message(picking, True)

    def test_05_price_variance_check_global_threshold_amount(self):
        self.company.price_variance_threshold_amount = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking, expect_error=True)

    def test_06_price_variance_check_global_threshold_percent(self):
        self.company.price_variance_threshold_percent = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking, expect_error=True)

    def test_07_global_price_variance_check_disable(self):
        self.company.enable_price_variance_error = False
        self.company.price_variance_threshold_percent = 5
        po = self.create_purchase_order(price_unit=110)
        po.button_confirm()
        picking = po.picking_ids
        self.validate_picking(picking)
        self.check_chatter_message(picking, True)
