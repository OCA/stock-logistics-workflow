# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockMoveValuationUsage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get required Model
        cls.product_model = cls.env["product.product"]
        cls.template_model = cls.env["product.template"]
        cls.product_ctg_model = cls.env["product.category"]
        cls.account_model = cls.env["account.account"]
        cls.res_users_model = cls.env["res.users"]
        # Get required Model data
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.company = cls.env.ref("base.main_company")
        cls.stock_picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.stock_location_id = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_customer_id = cls.env.ref("stock.stock_location_customers")
        cls.stock_location_supplier_id = cls.env.ref("stock.stock_location_suppliers")
        # Account types
        expense_type = "expense"
        asset_type = "asset_fixed"
        # Create account for Cost of Goods Sold
        name = "Cost of Goods Sold"
        code = "cogs"
        acc_type = expense_type
        cls.account_cogs = cls._create_account(acc_type, name, code, cls.company)
        # Create account for Inventory
        name = "Inventory"
        code = "inventory"
        acc_type = asset_type
        cls.account_inventory = cls._create_account(acc_type, name, code, cls.company)

        cls.stock_journal = cls.env["account.journal"].create(
            {"name": "Stock journal", "type": "general", "code": "STK00"}
        )
        # Create product category
        cls.product_ctg = cls._create_product_category()

        # Create partners
        cls.supplier = cls.env["res.partner"].create({"name": "Test supplier"})
        cls.customer = cls.env["res.partner"].create({"name": "Test customer"})

        # Create a Product with real cost
        standard_price = 10.0
        list_price = 20.0
        cls.product = cls._create_product(standard_price, False, list_price)

        # Create a vendor
        cls.vendor_partner = cls.env["res.partner"].create({"name": "dropship vendor"})

    @classmethod
    def _create_user(cls, login, groups, company):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = cls.res_users_model.with_context(no_reset_password=True).create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "test@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "group_ids": [(6, 0, group_ids)],
            }
        )
        return user

    @classmethod
    def _create_account(cls, acc_type, name, code, company):
        """Create an account."""
        account = cls.account_model.create(
            {
                "name": name,
                "code": code,
                "account_type": acc_type,
                "company_ids": [(6, 0, company.ids)],
            }
        )
        return account

    @classmethod
    def _create_product_category(cls):
        product_ctg = cls.product_ctg_model.create(
            {
                "name": "test_product_ctg",
                "property_stock_valuation_account_id": cls.account_inventory.id,
                "property_account_expense_categ_id": cls.account_cogs.id,
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_stock_journal": cls.stock_journal.id,
            }
        )
        return product_ctg

    @classmethod
    def _create_product(cls, standard_price, template, list_price):
        """Create a Product variant."""
        if not template:
            template = cls.template_model.create(
                {
                    "name": "test_product",
                    "categ_id": cls.product_ctg.id,
                    "is_storable": True,
                    "standard_price": standard_price,
                    "invoice_policy": "delivery",
                }
            )
            return template.product_variant_ids[0]
        product = cls.product_model.create(
            {"product_tmpl_id": template.id, "list_price": list_price}
        )
        return product

    def _create_delivery(
        self,
        product,
        qty,
    ):
        return self.env["stock.picking"].create(
            {
                "name": self.stock_picking_type_out.sequence_id._next(),
                "partner_id": self.customer.id,
                "picking_type_id": self.stock_picking_type_out.id,
                "location_id": self.stock_location_id.id,
                "location_dest_id": self.stock_location_customer_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.stock_location_id.id,
                            "location_dest_id": self.stock_location_customer_id.id,
                            "procure_method": "make_to_stock",
                        }
                    )
                ],
            }
        )

    def _create_drophip_picking(
        self,
        product,
        qty,
    ):
        return self.env["stock.picking"].create(
            {
                "name": self.stock_picking_type_out.sequence_id._next(),
                "partner_id": self.customer.id,
                "picking_type_id": self.stock_picking_type_out.id,
                "location_id": self.stock_location_supplier_id.id,
                "location_dest_id": self.stock_location_customer_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.stock_location_supplier_id.id,
                            "location_dest_id": self.stock_location_customer_id.id,
                        },
                    )
                ],
            }
        )

    def _create_receipt(self, product, qty, move_dest_id=None):
        move_dest_id = [(4, move_dest_id)] if move_dest_id else False
        return self.env["stock.picking"].create(
            {
                "name": self.stock_picking_type_in.sequence_id._next(),
                "partner_id": self.vendor_partner.id,
                "picking_type_id": self.stock_picking_type_in.id,
                "location_id": self.stock_location_supplier_id.id,
                "location_dest_id": self.stock_location_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "price_unit": 10.0,
                            "move_dest_ids": move_dest_id,
                            "location_id": self.stock_location_supplier_id.id,
                            "location_dest_id": self.stock_location_id.id,
                            "procure_method": "make_to_stock",
                        },
                    )
                ],
            }
        )

    def _do_picking(self, picking, date, qty):
        """Do picking with only one move on the given date."""
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = qty
        res = picking.button_validate()
        if isinstance(res, dict) and res:
            backorder_wiz_id = res["res_id"]
            backorder_wiz = self.env["stock.backorder.confirmation"].browse(
                [backorder_wiz_id]
            )
            backorder_wiz.process()
        return True

    def test_01_stock_receipt(self):
        """Receive into stock and ship to the customer"""
        # Create receipt
        in_picking = self._create_receipt(self.product, 1.0)
        # Receive one unit.
        self._do_picking(in_picking, fields.Datetime.now(), 1.0)

        # There's a stock move associated to this receipt
        move = in_picking.move_ids
        self.assertEqual(len(move), 1)
        self.assertEqual(move.remaining_qty, 1.0)
        self.assertEqual(move.remaining_value, 10.0)

        # Create an out picking
        out_picking = self._create_delivery(self.product, 1)
        self._do_picking(out_picking, fields.Datetime.now(), 1.0)
        # The original move must have been reduced.
        self.assertEqual(move.remaining_qty, 0.0)
        self.assertEqual(move.remaining_value, 0.0)
        # The original move is referenced in the outbound move
        valuation_usage = out_picking.move_ids.incoming_usage_ids
        self.assertEqual(len(valuation_usage), 1)
        self.assertEqual(valuation_usage.quantity, 1.0)
        self.assertEqual(valuation_usage.value, 10.0)
        self.assertEqual(valuation_usage.src_stock_move_id, move)

    def test_02_drop_ship(self):
        """Drop shipment from vendor to customer"""
        # Create drop_shipment
        dropship_picking = self._create_drophip_picking(self.product, 1.0)
        # Receive one unit.
        self._do_picking(dropship_picking, fields.Datetime.now(), 1.0)

        # There's a stock move associated to this dropship
        move = dropship_picking.move_ids
        self.assertEqual(len(move), 1)
        # Dropship moves have both in and out characteristics
        self.assertTrue(move.is_dropship)
        # The move should have valuation usage tracking
        valuation_usage = move.incoming_usage_ids
        self.assertEqual(len(valuation_usage), 1)
        self.assertEqual(valuation_usage.quantity, 1.0)
        self.assertEqual(valuation_usage.value, 10.0)
        self.assertEqual(valuation_usage.src_stock_move_id, move)
        self.assertEqual(valuation_usage.dest_stock_move_id, move)
        # Verify incoming and outgoing usage links
        self.assertEqual(
            move.incoming_usage_ids.mapped("src_stock_move_id").ids,
            [move.id],
        )
        self.assertEqual(
            move.usage_ids.mapped("dest_stock_move_id").ids,
            [move.id],
        )

    def test_03_revaluation_of_negative_fifo(self):
        out_picking = self._create_delivery(self.product, 10)
        self._do_picking(out_picking, fields.Datetime.now(), 10.0)
        out_move = out_picking.move_ids
        remaining_qty = out_move.remaining_qty
        self.assertTrue(remaining_qty == 0.0)
        in_picking = self._create_receipt(self.product, 10.0)
        self._do_picking(in_picking, fields.Datetime.now(), 10.0)
        in_move = in_picking.move_ids
        out_picking = self.env["stock.picking"].browse(out_picking.id)
        remaining_qty = out_move.remaining_qty
        self.assertEqual(remaining_qty, 0)
        self.assertEqual(out_move.incoming_usage_ids.src_stock_move_id, in_move)

    def test_04_multiple_incoming_consumed_by_single_outgoing(self):
        """Test one outgoing consuming from multiple incoming receipts.

        Scenario:
        - wh/in/1: 1 unit
        - wh/in/2: 1 unit
        - wh/out/1: 2 units (consumes from both)

        Expected: 2 valuation_usage records (one for each incoming)
        """
        # Create and receive first incoming (1 unit)
        in_picking1 = self._create_receipt(self.product, 1.0)
        self._do_picking(in_picking1, fields.Datetime.now(), 1.0)
        in_move1 = in_picking1.move_ids

        # Create and receive second incoming (1 unit)
        in_picking2 = self._create_receipt(self.product, 1.0)
        self._do_picking(in_picking2, fields.Datetime.now(), 1.0)
        in_move2 = in_picking2.move_ids

        # Create outgoing for 2 units
        out_picking = self._create_delivery(self.product, 2)
        self._do_picking(out_picking, fields.Datetime.now(), 2.0)
        out_move = out_picking.move_ids

        # Should have 2 valuation_usage records
        valuation_usage = out_move.incoming_usage_ids
        self.assertEqual(len(valuation_usage), 2)

        # Verify both incomings are referenced
        move_ids = valuation_usage.mapped("src_stock_move_id").ids
        self.assertIn(in_move1.id, move_ids)
        self.assertIn(in_move2.id, move_ids)
