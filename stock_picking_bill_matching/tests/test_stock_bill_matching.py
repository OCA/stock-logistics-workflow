# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestStockBillMatching(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_a = cls.env["res.partner"].create({"name": "Test Vendor Partner"})
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Test Product A",
                "type": "product",
                "standard_price": 50.0,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Test Product B",
                "type": "product",
                "standard_price": 100.0,
            }
        )

        # Get the default incoming picking type for the main company
        cls.picking_type_in = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "incoming"),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )

    def create_picking(self, products_info):
        """Helper to create and process an incoming picking."""
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_a.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.picking_type_in.default_location_dest_id.id,
            }
        )
        for product, qty in products_info:
            self.env["stock.move"].create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                }
            )
        picking.action_confirm()
        picking.action_assign()
        return picking

    def create_bill(self, products_info):
        """Helper to create a draft vendor bill."""
        return self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": qty,
                            "price_unit": price,
                        },
                    )
                    for product, qty, price in products_info
                ],
            }
        )

    def test_01_partial_match_and_backorder(self):
        """Test matching partial quantities automatically creates backorders."""
        # 1. Create a Picking with 10 units
        picking = self.create_picking([(self.product_a, 10)])

        # 2. Create a Bill for only 4 units
        self.create_bill([(self.product_a, 4, 50.0)])

        # Flush memory to DB so the SQL View can see the records!
        self.env.flush_all()

        # Find the lines in the matching view
        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        self.assertEqual(
            len(match_lines), 2, "Should find 1 stock move and 1 bill line."
        )

        # 3. Trigger Match
        match_lines.action_match_lines()

        # 4. Check that the original picking is Done with 4 units
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity_done, 4)

        # 5. Check that a Backorder was created for the remaining 6 units
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(backorder, "A backorder should have been generated.")
        self.assertEqual(
            backorder.move_ids.product_uom_qty, 6, "Backorder should have 6 units."
        )

    def test_02_unmatch_lines(self):
        """Test the undo/unmatch feature severs the M2M link cleanly."""
        self.create_picking([(self.product_a, 5)])
        bill = self.create_bill([(self.product_a, 5, 50.0)])

        match_lines = self.env["picking.bill.line.match"].search(
            [("partner_id", "=", self.partner_a.id)]
        )
        match_lines.action_match_lines()

        self.assertTrue(bill.invoice_line_ids.move_line_ids, "M2M should be linked.")

        # Find the matched lines and unmatch
        matched_lines = self.env["picking.bill.line.match"].search(
            [("partner_id", "=", self.partner_a.id), ("is_matched", "=", True)]
        )
        matched_lines.action_unmatch_lines()
        self.assertFalse(
            bill.invoice_line_ids.move_line_ids, "M2M link should be severed."
        )

    def test_03_perfect_match_automation(self):
        """Condition A: If a single bill and picking match perfectly, auto-link them."""
        # 1. Create matching picking and bill
        picking = self.create_picking([(self.product_b, 15)])
        bill = self.create_bill([(self.product_b, 15, 100.0)])

        # 2. Trigger the smart button
        action = bill.action_picking_matching()

        # 3. Assert it bypassed the SQL view and jumped straight to the picking
        self.assertEqual(
            action.get("res_model"),
            "stock.picking",
            "Should return the picking form directly.",
        )
        self.assertEqual(action.get("res_id"), picking.id)

        # 4. Assert the M2M link was properly created
        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)

        # 5. Assert Duck Typing update (if `stock_picking_invoicing` is installed in this env)
        if hasattr(self.env["stock.move"], "invoice_state"):
            self.assertEqual(picking.invoice_state, "invoiced")

    def test_04_auto_create_automation(self):
        """Condition B: Auto-create a picking from a bill if configured."""
        # 1. Enable company setting
        self.env.company.auto_create_picking_on_match = True
        self.env.company.auto_validate_matched_picking = True

        # 2. Create a bill with NO matching pickings or POs
        bill = self.create_bill([(self.product_b, 8, 100.0)])

        # 3. Trigger smart button
        action = bill.action_picking_matching()

        # 4. Assert it auto-generated a picking and returned it
        self.assertEqual(action.get("res_model"), "stock.picking")
        new_picking_id = action.get("res_id")
        self.assertTrue(new_picking_id, "A new picking should have been generated.")

        new_picking = self.env["stock.picking"].browse(new_picking_id)
        self.assertEqual(new_picking.state, "done", "It should be auto-validated.")
        self.assertEqual(new_picking.move_ids.product_uom_qty, 8)
        self.assertEqual(
            bill.invoice_line_ids.move_line_ids,
            new_picking.move_ids,
            "M2M should be linked.",
        )

    def test_05_service_lines_excluded(self):
        """Service lines should not appear in the matching view and should
        not block matching of storable lines."""
        service_product = self.env.ref("product.product_product_1")
        self.assertEqual(service_product.type, "service")

        picking = self.create_picking([(self.product_a, 5)])
        bill = self.create_bill(
            [(self.product_a, 5, 50.0), (service_product, 1, 100.0)]
        )

        self.env.flush_all()

        # Only 2 lines (1 stock move + 1 storable bill line) should be visible
        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "in", (self.product_a.id, service_product.id)),
            ]
        )
        self.assertEqual(
            len(match_lines),
            2,
            "Service bill lines must be excluded from the matching view.",
        )
        self.assertNotIn(
            service_product.id,
            match_lines.mapped("product_id").ids,
            "Service product should not appear in matching view.",
        )

        # Matching should succeed without touching the service line
        match_lines.action_match_lines()
        self.assertEqual(
            bill.invoice_line_ids.filtered(
                lambda l: l.product_id == self.product_a
            ).move_line_ids,
            picking.move_ids,
        )
        self.assertTrue(
            bill.is_picking_matched,
            "Mixed bill with matched storable lines should be considered matched.",
        )

        # Auto-match bypass should also work with mixed bills
        bill2 = self.create_bill(
            [(self.product_a, 5, 50.0), (service_product, 1, 100.0)]
        )
        picking2 = self.create_picking([(self.product_a, 5)])
        self.env.flush_all()
        action = bill2.action_picking_matching()
        self.assertEqual(
            action.get("res_model"),
            "stock.picking",
            "Auto-match bypass should work when storable lines match.",
        )
        self.assertEqual(action.get("res_id"), picking2.id)

    def test_06_force_matched_after_backorder_cancel(self):
        """If a receipt exceeds the billed qty and its backorder is cancelled,
        the user can force the bill to matched."""
        picking = self.create_picking([(self.product_a, 10)])
        bill = self.create_bill([(self.product_a, 4, 50.0)])

        self.env.flush_all()
        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        match_lines.action_match_lines()

        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(backorder)
        backorder.action_cancel()

        # After matching 4 out of 4 billed, bill is still matched
        self.assertTrue(bill.is_picking_matched)

        # Force matched remains an idempotent safe fallback
        bill.action_force_picking_matched()
        self.assertTrue(bill.force_picking_matched)
        self.assertTrue(bill.is_picking_matched)

    def test_07_force_matched_when_bill_exceeds_receipt(self):
        """If a bill has a higher quantity than the receipt and no further
        receipts are expected, the user can force the bill to matched."""
        self.create_picking([(self.product_a, 4)])
        bill = self.create_bill([(self.product_a, 10, 50.0)])

        self.env.flush_all()
        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        match_lines.action_match_lines()

        # Only 4 out of 10 billed units are matched -> not fully matched
        self.assertFalse(
            bill.is_picking_matched,
            "Bill should stay unmatched when billed qty exceeds receipt qty.",
        )

        # User decides no further receipts will come
        bill.action_force_picking_matched()
        self.assertTrue(bill.force_picking_matched)
        self.assertTrue(
            bill.is_picking_matched,
            "Force matched should override the unmatched state.",
        )

    def test_08_no_product_lines_excluded(self):
        """Bill lines without a product should be excluded from matching
        and should not block the bill from being considered matched."""
        self.create_picking([(self.product_a, 5)])
        bill = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "display_type": "product",
                            "name": "Line without product",
                            "quantity": 2,
                            "price_unit": 100.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "quantity": 5,
                            "price_unit": 50.0,
                        },
                    ),
                ],
            }
        )

        self.env.flush_all()

        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("account_move_id", "=", bill.id),
            ]
        )
        self.assertEqual(
            len(match_lines),
            2,
            "Only storable bill line + stock move should appear in view.",
        )
        self.assertFalse(
            any(not line.product_id for line in match_lines),
            "Lines without product must not appear in matching view.",
        )

        match_lines.action_match_lines()
        self.assertTrue(
            bill.is_picking_matched,
            "Bill should be matched when storable lines are matched "
            "even if a no-product line exists.",
        )
