# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command, _, fields
from odoo.exceptions import AccessError, UserError
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

    def test_09_consumable_lines(self):
        """Consumable lines should appear in the matching view but should
        not prevent the bill from being considered matched."""
        consumable = self.env["product.product"].create(
            {
                "name": "Test Consumable",
                "type": "consu",
                "standard_price": 20.0,
            }
        )
        self.create_picking([(self.product_a, 5)])
        bill = self.create_bill([(self.product_a, 5, 50.0), (consumable, 3, 20.0)])

        self.env.flush_all()

        # Consumable should still appear in the matching view
        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "in", (self.product_a.id, consumable.id)),
                ("is_matched", "=", False),
            ]
        )
        self.assertIn(
            consumable.id,
            match_lines.mapped("product_id").ids,
            "Consumable line should appear in matching view.",
        )

        # Match only the storable line
        storable_lines = match_lines.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(storable_lines), 2)
        storable_lines.action_match_lines()

        # Policy (pinned by test_21_consumables_policy): every line listed in
        # the matching screen must be matched for the bill to count as
        # matched, consumables included.
        self.assertFalse(
            bill.is_picking_matched,
            "the unmatched consumable line keeps the bill unmatched",
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
                # Same domain as ``action_picking_matching``: the bill own lines
                # plus the receipt lines, whose ``account_move_id`` is empty until
                # they get matched.
                ("account_move_id", "in", (bill.id, False)),
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

    # ------------------------------------------------------------------
    # Already received goods (the bill arrives after the goods): the
    # matching must LINK those receipts, never validate them again.
    # ------------------------------------------------------------------

    def _validate_picking(self, picking):
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking._action_done()
        self.assertEqual(picking.state, "done")

    def _set_reference(self, aml_or_move, reference):
        """The reference the localization fills (xPed/nItemPed, or the one
        synthesized by the fiscal document import wizard)."""
        aml_or_move.matching_reference = reference

    def test_10_done_receipt_can_be_matched(self):
        """A bill must be matchable against an ALREADY validated receipt.

        Regression: the engine only considered draft/confirmed/assigned moves
        and computed the linkage quantity as ``product_uom_qty -
        quantity_done`` (always 0 once done), so the screen listed the pair
        and clicking Match Selected silently did nothing.
        """
        picking = self.create_picking([(self.product_a, 10)])
        self._validate_picking(picking)
        bill = self.create_bill([(self.product_a, 10, 50.0)])
        self.env.flush_all()

        match_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        self.assertEqual(len(match_lines), 2, "bill line + done receipt line")
        self.assertTrue(match_lines.filtered("sm_id").is_done)

        match_lines.action_match_lines()

        self.assertEqual(
            bill.invoice_line_ids.move_line_ids,
            picking.move_ids,
            "the done receipt line must be linked to the bill line",
        )
        self.assertTrue(bill.is_picking_matched)
        # the receipt is NOT validated again, and no backorder is created
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity_done, 10)
        self.assertFalse(
            self.env["stock.picking"].search([("backorder_id", "=", picking.id)])
        )

    def test_11_done_receipt_smart_button(self):
        """The Match Pickings button also reconciles an already done receipt
        (its quantities are equal, so the perfect-match shortcut links it)."""
        picking = self.create_picking([(self.product_b, 15)])
        self._validate_picking(picking)
        bill = self.create_bill([(self.product_b, 15, 100.0)])
        self.env.flush_all()

        action = bill.action_picking_matching()
        self.assertEqual(action.get("res_model"), "stock.picking")
        self.assertEqual(action.get("res_id"), picking.id)
        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)

    # ------------------------------------------------------------------
    # Reference driven automatic matching (deterministic only)
    # ------------------------------------------------------------------

    def test_12_auto_match_referenced_lines_on_button(self):
        """With the flag on, the lines whose reference is shared by a receipt
        line are matched by the Match Pickings button, without any click in
        the screen; the action is traced in the chatter."""
        self.env.company.auto_match_referenced_lines = True
        picking = self.create_picking([(self.product_a, 6)])
        self._set_reference(picking.move_ids, "P00129-1")
        bill = self.create_bill([(self.product_a, 6, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00129-1")
        self.env.flush_all()

        bill.action_picking_matching()

        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)
        self.assertTrue(bill.is_picking_matched)
        self.assertIn(
            "automatically matched",
            " ".join(bill.message_ids.mapped("body")),
            "the automatic matching must be traced in the chatter",
        )

    def test_13_auto_match_requires_a_reference(self):
        """No reference, no automatic matching: a wrong automatic link is
        worse than a manual click.

        The quantities are deliberately different, so the module's unrelated
        'perfect match' shortcut cannot hide the behaviour under test.
        """
        self.env.company.auto_match_referenced_lines = True
        self.create_picking([(self.product_a, 4)])
        bill = self.create_bill([(self.product_a, 5, 50.0)])
        self.env.flush_all()

        action = bill.action_picking_matching()

        self.assertEqual(
            action.get("res_model"),
            "picking.bill.line.match",
            "without references the operator still gets the matching screen",
        )
        self.assertFalse(bill.invoice_line_ids.move_line_ids)
        self.assertFalse(bill.is_picking_matched)

    def test_14_auto_match_does_not_cross_match_references(self):
        """A receipt whose reference differs must not be consumed, even for
        the same product and the same partner."""
        self.env.company.auto_match_referenced_lines = True
        matching = self.create_picking([(self.product_a, 4)])
        self._set_reference(matching.move_ids, "P00129-1")
        other = self.create_picking([(self.product_a, 4)])
        self._set_reference(other.move_ids, "P00129-2")
        bill = self.create_bill([(self.product_a, 4, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00129-1")
        self.env.flush_all()

        bill.action_picking_matching()

        self.assertEqual(bill.invoice_line_ids.move_line_ids, matching.move_ids)
        self.assertFalse(
            other.move_ids & bill.invoice_line_ids.move_line_ids,
            "the receipt of another reference must stay untouched",
        )
        self.assertEqual(other.move_ids.unmatched_qty, 4)

    def test_15_auto_match_on_bill_post(self):
        """With auto_match_referenced_on_post the bill is reconciled when it
        is posted, without any click."""
        self.env.company.auto_match_referenced_lines = True
        self.env.company.auto_match_referenced_on_post = True
        picking = self.create_picking([(self.product_a, 3)])
        self._set_reference(picking.move_ids, "P00129-3")
        bill = self.create_bill([(self.product_a, 3, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00129-3")
        self.env.flush_all()

        bill.action_post()

        self.assertEqual(bill.state, "posted")
        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)
        self.assertTrue(bill.is_picking_matched)

    def test_16_auto_match_off_by_default(self):
        """Nothing happens when the company did not opt in.

        Unequal quantities on purpose: the 'perfect match' shortcut is an
        unrelated, pre-existing feature that would otherwise match the line
        and mask what this test measures.
        """
        self.create_picking([(self.product_a, 5)])
        bill = self.create_bill([(self.product_a, 3, 50.0)])
        self.env.flush_all()

        bill.action_post()

        self.assertFalse(bill.invoice_line_ids.move_line_ids)
        self.assertFalse(bill.is_picking_matched)
        bill.action_picking_matching()
        # the on-button path honours the same flag
        self.assertFalse(bill.invoice_line_ids.move_line_ids)

    # ------------------------------------------------------------------
    # Smart button counters
    # ------------------------------------------------------------------

    def test_17_matching_counters(self):
        """The smart buttons count what the operator still has to do."""
        self.create_picking([(self.product_a, 5)])
        bill = self.create_bill([(self.product_a, 5, 50.0), (self.product_b, 2, 100.0)])
        self.env.flush_all()

        self.assertEqual(
            bill.unmatched_line_count,
            2,
            "two product lines to match (the second one has no receipt at all)",
        )
        self.assertEqual(bill.matched_picking_line_count, 0)

        # match the storable line only
        lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        lines.action_match_lines()

        self.assertEqual(bill.unmatched_line_count, 1)
        self.assertEqual(bill.matched_picking_line_count, 1)
        # a forced bill shows no counter either way: it is settled
        bill.action_force_picking_matched()
        self.assertTrue(bill.is_picking_matched)

    # ------------------------------------------------------------------
    # Security, wizard and isolation
    # ------------------------------------------------------------------

    def test_18_stock_user_can_read_the_matching_screen(self):
        """The smart buttons are shown to stock users, so the matching model
        must be readable by them (it used to be accountant-only)."""
        stock_user = self.env["res.users"].create(
            {
                "name": "Warehouse Only",
                "login": "warehouse_only_test",
                "groups_id": [
                    Command.set(
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("stock.group_stock_user").id,
                        ]
                    )
                ],
            }
        )
        plain_user = self.env["res.users"].create(
            {
                "name": "No Stock No Account",
                "login": "plain_user_test",
                "groups_id": [Command.set([self.env.ref("base.group_user").id])],
            }
        )
        match_model = self.env["picking.bill.line.match"]
        # must not raise
        match_model.with_user(stock_user).check_access_rights("read")
        self.assertTrue(match_model.with_user(stock_user).search([]) is not None)
        with self.assertRaises(AccessError):
            match_model.with_user(plain_user).check_access_rights("read")

    def test_19_wizard_adds_bill_lines_to_an_existing_picking(self):
        """The Create / Add to Picking wizard can feed an existing receipt."""
        existing = self.create_picking([(self.product_b, 1)])
        bill = self.create_bill([(self.product_a, 2, 50.0)])
        self.env.flush_all()

        lines = self.env["picking.bill.line.match"].search(
            [("aml_id", "in", bill.invoice_line_ids.ids)]
        )
        action = lines.action_add_to_picking()
        wizard = (
            self.env["bill.to.picking.wizard"]
            .with_context(**action["context"])
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "picking_id": existing.id,
                }
            )
        )
        wizard.action_add_to_picking()

        new_moves = existing.move_ids - existing.move_ids.filtered(
            lambda m: m.product_id == self.product_b
        )
        self.assertEqual(new_moves.product_id, self.product_a)
        self.assertEqual(new_moves.product_uom_qty, 2)
        self.assertEqual(bill.invoice_line_ids.move_line_ids, new_moves)

    def test_20_two_bills_of_the_same_partner_are_isolated(self):
        """Each bill is matched against its own reference only."""
        self.env.company.auto_match_referenced_lines = True
        first_picking = self.create_picking([(self.product_a, 2)])
        self._set_reference(first_picking.move_ids, "P00001-1")
        second_picking = self.create_picking([(self.product_a, 2)])
        self._set_reference(second_picking.move_ids, "P00002-1")

        first_bill = self.create_bill([(self.product_a, 2, 50.0)])
        self._set_reference(first_bill.invoice_line_ids, "P00001-1")
        second_bill = self.create_bill([(self.product_a, 2, 50.0)])
        self._set_reference(second_bill.invoice_line_ids, "P00002-1")
        self.env.flush_all()

        first_bill.action_picking_matching()
        second_bill.action_picking_matching()

        self.assertEqual(
            first_bill.invoice_line_ids.move_line_ids, first_picking.move_ids
        )
        self.assertEqual(
            second_bill.invoice_line_ids.move_line_ids, second_picking.move_ids
        )

    def test_21_consumables_policy(self):
        """Policy, pinned: every line listed in the matching screen must be
        matched for the bill to count as matched — including consumables,
        which are received like storable products."""
        consumable = self.env["product.product"].create(
            {"name": "Policy Consumable", "type": "consu", "standard_price": 1.0}
        )
        self.create_picking([(self.product_a, 1)])
        bill = self.create_bill([(self.product_a, 1, 50.0), (consumable, 1, 1.0)])
        self.env.flush_all()

        lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", consumable.id),
            ]
        )
        self.assertTrue(lines, "the consumable line is listed for matching")

        storable_lines = self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )
        storable_lines.action_match_lines()
        self.assertFalse(
            bill.is_picking_matched,
            "the unmatched consumable line keeps the bill unmatched",
        )

    # ------------------------------------------------------------------
    # Ordering of the matching screen
    # ------------------------------------------------------------------

    def _match_rows_of_product(self):
        return self.env["picking.bill.line.match"].search(
            [
                ("partner_id", "=", self.partner_a.id),
                ("product_id", "=", self.product_a.id),
                ("is_matched", "=", False),
            ]
        )

    def test_26_group_order_follows_the_pairing_reference(self):
        """Inside a product group a vendor bill line is immediately followed
        by the receipt line carrying the same Match Ref; the lines that could
        not be paired (no reference, or a reference no bill line carries) come
        last, vendor bills still before receipts."""
        first_receipt = self.create_picking([(self.product_a, 5)])
        self._set_reference(first_receipt.move_ids, "P001-1")
        second_receipt = self.create_picking([(self.product_a, 5)])
        self._set_reference(second_receipt.move_ids, "P001-2")
        orphan_receipt = self.create_picking([(self.product_a, 5)])
        self._set_reference(orphan_receipt.move_ids, "P002-9")

        bill = self.create_bill([(self.product_a, 5, 50.0)] * 3)
        self._set_reference(bill.invoice_line_ids[0], "P001-1")
        self._set_reference(bill.invoice_line_ids[1], "P001-2")
        # the third bill line keeps no reference: nothing can pair it
        self.env.flush_all()

        rows = self._match_rows_of_product()
        self.assertEqual(
            [(row.line_type, row.matching_reference or False) for row in rows],
            [
                ("vendor_bill", "P001-1"),
                ("stock_move", "P001-1"),
                ("vendor_bill", "P001-2"),
                ("stock_move", "P001-2"),
                ("vendor_bill", False),
                ("stock_move", "P002-9"),
            ],
            "each bill line must be followed by its own receipt line",
        )
        self.assertEqual(
            [row.pair_rank for row in rows],
            [0, 0, 1, 1, 0, 0],
            "paired lines share a rank",
        )
        # the unpaired rows must have NO rank at all (NULL), not rank 0: that
        # is what PostgreSQL sorts last. The ORM reads the NULL as 0 for an
        # Integer field, so check the raw value (this model is not a database
        # view: Odoo inlines its _table_query, hence the wrapper).
        match_model = self.env["picking.bill.line.match"]
        self.env.cr.execute(
            f"SELECT bool_and(pair_rank IS NULL) FROM ({match_model._table_query})"
            " AS m WHERE m.id IN %s",
            (tuple(rows[-2:].ids),),
        )
        self.assertTrue(
            self.env.cr.fetchone()[0],
            "an unpaired line (no reference, or a reference no bill line "
            "carries) must have a NULL rank to be sorted last",
        )

    def test_27_group_order_keeps_same_reference_lines_together(self):
        """Several bill lines and several receipts sharing one reference stay
        adjacent, the bills first: that is a supplier splitting an order line
        over two invoice lines, received in two shipments."""
        first_receipt = self.create_picking([(self.product_a, 4)])
        self._set_reference(first_receipt.move_ids, "P001-1")
        second_receipt = self.create_picking([(self.product_a, 6)])
        self._set_reference(second_receipt.move_ids, "P001-1")
        other_receipt = self.create_picking([(self.product_a, 1)])
        self._set_reference(other_receipt.move_ids, "P001-2")

        bill = self.create_bill([(self.product_a, 4, 50.0), (self.product_a, 6, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P001-1")
        self.env.flush_all()

        rows = self._match_rows_of_product()
        self.assertEqual(
            [(row.line_type, row.matching_reference) for row in rows],
            [
                ("vendor_bill", "P001-1"),
                ("vendor_bill", "P001-1"),
                ("stock_move", "P001-1"),
                ("stock_move", "P001-1"),
                ("stock_move", "P001-2"),
            ],
            "the group of the reference comes first, the other receipt last",
        )

    def _create_mixed_bill(self, service):
        """A vendor bill carrying every kind of non matchable line."""
        return self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {"display_type": "line_section", "name": "A section"}
                    ),
                    Command.create({"display_type": "line_note", "name": "A note"}),
                    Command.create(
                        {
                            "product_id": service.id,
                            "name": "A service",
                            "quantity": 1,
                            "price_unit": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "quantity": 4,
                            "price_unit": 50.0,
                        }
                    ),
                ],
            }
        )

    def test_22_cosmetic_and_service_lines_are_ignored(self):
        """Sections, notes and services are neither matched nor counted, and
        they never keep a bill unmatched."""
        service = self.env["product.product"].create(
            {"name": "Ignored Service", "type": "service"}
        )
        picking = self.create_picking([(self.product_a, 4)])
        bill = self._create_mixed_bill(service)
        self.env.flush_all()

        # a) the matching screen only lists the real product line
        rows = self.env["picking.bill.line.match"].search(
            [("partner_id", "=", self.partner_a.id)]
        )
        self.assertEqual(len(rows), 2, "one bill line + its receipt line")
        self.assertEqual(rows.mapped("product_id"), self.product_a)

        # b) counters and matched state ignore them
        self.assertEqual(bill.unmatched_line_count, 1)
        self.assertEqual(bill.matched_picking_line_count, 0)
        self.assertFalse(bill.is_picking_matched)

        # c) the automatic matching has no candidate on a service line, even
        #    when it carries a reference
        self.env.company.auto_match_referenced_lines = True
        service_line = bill.invoice_line_ids.filtered(
            lambda line: line.product_id == service
        )
        service_line.matching_reference = "P00129-9"
        bill_lines, receipt_lines = bill._get_referenced_candidates()
        self.assertFalse(bill_lines, "a service line is never an auto-match line")
        self.assertFalse(receipt_lines)
        self.env.company.auto_match_referenced_lines = False

        # d) matching the product line is enough: the cosmetic lines do not
        #    block the bill, and the service line stays out of the links
        bill.action_picking_matching()
        self.assertTrue(bill.is_picking_matched)
        self.assertEqual(bill.unmatched_line_count, 0)
        self.assertEqual(bill.matched_picking_line_count, 1)
        self.assertEqual(
            bill.invoice_line_ids.mapped("move_line_ids"), picking.move_ids
        )
        self.assertFalse(service_line.move_line_ids)

    def test_23_all_matched_notification(self):
        """Clicking Match Pickings when nothing is left to match says so and
        reloads the bill instead of opening an empty screen."""
        self.env.company.auto_match_referenced_lines = True
        picking = self.create_picking([(self.product_a, 2)])
        self._set_reference(picking.move_ids, "P00129-5")
        bill = self.create_bill([(self.product_a, 2, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00129-5")
        self.env.flush_all()

        action = bill.action_picking_matching()

        self.assertEqual(action.get("tag"), "display_notification")
        self.assertIn("matched", action["params"]["message"].lower())
        reload_action = action["params"]["next"]
        self.assertEqual(reload_action["res_model"], "account.move")
        self.assertEqual(reload_action["res_id"], bill.id)
        self.assertTrue(bill.is_picking_matched)

    def test_24_generated_receipt_is_traceable(self):
        """A receipt generated by the module carries its bill as origin and a
        chatter message explaining the automatic creation, with a link back to
        the bill."""
        self.env.company.auto_create_picking_on_match = True
        self.env.company.auto_validate_matched_picking = True
        bill = self.create_bill([(self.product_a, 8, 50.0)])
        self.env.flush_all()

        action = bill.action_picking_matching()

        self.assertEqual(action.get("res_model"), "stock.picking")
        picking = self.env["stock.picking"].browse(action["res_id"])
        # depending on the database, a draft bill is already numbered or still
        # named '/' (the CI keeps it unnamed): what must hold in both cases is a
        # meaningful label, never the '/' placeholder
        self.assertTrue(picking.origin.endswith(" (bill matching)"))
        self.assertNotEqual(picking.origin, "/ (bill matching)")
        self.assertEqual(picking.state, "done")
        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)
        body = " ".join(picking.message_ids.mapped("body"))
        self.assertIn("created by the bill matching wizard", body)
        self.assertIn("automatically", body)
        self.assertIn("data-oe-model", body, "the bill must be linked")
        self.assertIn(str(bill.id), body)

        # a bill still named '/' (what the fiscal import produces here) must
        # not leak a '/' origin: its display name identifies it instead
        nameless = self.create_bill([(self.product_a, 1, 50.0)])
        nameless.name = "/"
        wizard = self.env["bill.to.picking.wizard"].create(
            {"partner_id": self.partner_a.id}
        )
        self.assertEqual(wizard._get_bill_label(nameless), nameless.display_name)
        self.assertIn(str(nameless.id), wizard._get_bill_label(nameless))

    def test_25_wizard_generated_receipt_is_traceable(self):
        """The same traceability when the operator generates the receipt from
        the matching screen (the manual path), and for a posted bill the real
        bill name is used as origin."""
        bill = self.create_bill([(self.product_a, 2, 50.0)])
        bill.action_post()
        self.assertTrue(bill.name and bill.name != "/")
        self.env.flush_all()

        lines = self.env["picking.bill.line.match"].search(
            [("aml_id", "in", bill.invoice_line_ids.ids)]
        )
        self.assertTrue(lines)
        action = lines.action_add_to_picking()
        wizard = (
            self.env["bill.to.picking.wizard"]
            .with_context(**action["context"])
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "auto_validate": False,
                }
            )
        )
        wizard.action_add_to_picking()

        picking = wizard.picking_id
        self.assertEqual(picking.origin, "%s (bill matching)" % bill.name)
        self.assertNotEqual(
            picking.state,
            "done",
            "without auto-validation the generated receipt is only assigned",
        )
        body = " ".join(picking.message_ids.mapped("body"))
        self.assertIn("created by the bill matching wizard", body)
        self.assertIn("waiting to be received", body)
        self.assertIn(bill.name, body)
        self.assertIn("data-oe-model", body, "the bill must be linked")

    def test_28_shared_receipt_does_not_make_bill_lines_negative(self):
        """A receipt line shared by several bill lines must not give them a
        negative 'unmatched quantity'.

        One receipt line of 4 covering two bill lines of 2 (the supplier
        splitting an order line, or two deliveries in one receipt): each bill
        line is linked to the whole receipt line, so a plain subtraction would
        read -2 on both — meaningless for the operator, and the screen is
        where they verify their work.
        """
        picking = self.create_picking([(self.product_a, 4)])
        bill = self.create_bill([(self.product_a, 2, 50.0), (self.product_a, 2, 50.0)])
        self.env.flush_all()
        self.assertEqual(len(self._match_rows_of_product()), 3)

        self._match_rows_of_product().action_match_lines()
        self.env.flush_all()

        self.assertEqual(
            bill.invoice_line_ids.mapped("unmatched_qty"),
            [0.0, 0.0],
            "a bill line can never have a negative quantity left to match",
        )
        self.assertEqual(picking.move_ids.unmatched_qty, 0.0)
        self.assertTrue(bill.is_picking_matched)
        # and the screen shows nothing left on either side
        self.assertFalse(
            self.env["picking.bill.line.match"].search(
                [
                    ("product_id", "=", self.product_a.id),
                    ("unmatched_qty", ">", 0.001),
                ]
            ),
            "nothing is left to match once the receipt covers the bill lines",
        )

    def test_29_receipt_keeps_the_over_billing_sign(self):
        """The receipt side keeps the sign of its unmatched quantity: billed
        beyond what was received is exactly the anomaly to see."""
        bill = self.create_bill([(self.product_b, 6, 100.0)])
        receipt = self.create_picking([(self.product_b, 4)])
        self.env.flush_all()

        rows = self.env["picking.bill.line.match"].search(
            [
                ("product_id", "=", self.product_b.id),
                ("is_matched", "=", False),
            ]
        )
        rows.action_match_lines()
        self.env.flush_all()

        self.assertEqual(
            bill.invoice_line_ids.unmatched_qty,
            2.0,
            "the bill line still has 2 units to cover",
        )
        self.assertEqual(
            receipt.move_ids.unmatched_qty,
            -2.0,
            "the receipt line was billed beyond what was received",
        )
        self.assertFalse(bill.is_picking_matched)

    def test_30_a_reference_shared_by_several_receipts_prefers_the_received_one(self):
        """A reference identifies an order line, not a shipment: when a PO
        line was received in two shipments (one already done, one still
        pending), a bill for the received quantity must match the done one and
        leave the pending shipment untouched — not validate it."""
        done_receipt = self.create_picking([(self.product_a, 4)])
        self._validate_picking(done_receipt)
        self._set_reference(done_receipt.move_ids, "P00235-1")
        planned_receipt = self.create_picking([(self.product_a, 6)])
        self._set_reference(planned_receipt.move_ids, "P00235-1")

        bill = self.create_bill([(self.product_a, 4, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00235-1")
        self.env.company.auto_match_referenced_lines = True
        self.env.flush_all()

        bill.action_picking_matching()

        self.assertEqual(
            bill.invoice_line_ids.move_line_ids,
            done_receipt.move_ids,
            "the shipment already received must be matched first",
        )
        self.assertTrue(bill.is_picking_matched)
        self.assertEqual(
            planned_receipt.state,
            "assigned",
            "a pending shipment must not be validated to cover a bill it "
            "does not correspond to",
        )
        self.assertEqual(planned_receipt.move_ids.unmatched_qty, 6.0)

    def test_31_a_reference_shared_by_several_receipts_consumes_them_in_order(self):
        """The same reference covering more than the received shipment: the
        pending shipment of that order line is consumed (and received, which is
        the matching behaviour) after the done one is exhausted."""
        done_receipt = self.create_picking([(self.product_a, 4)])
        self._validate_picking(done_receipt)
        self._set_reference(done_receipt.move_ids, "P00235-1")
        planned_receipt = self.create_picking([(self.product_a, 6)])
        self._set_reference(planned_receipt.move_ids, "P00235-1")

        bill = self.create_bill([(self.product_a, 10, 50.0)])
        self._set_reference(bill.invoice_line_ids, "P00235-1")
        self.env.company.auto_match_referenced_lines = True
        self.env.flush_all()

        bill.action_picking_matching()

        self.assertEqual(
            bill.invoice_line_ids.move_line_ids,
            done_receipt.move_ids | planned_receipt.move_ids,
            "both shipments of the order line are consumed, the done one first",
        )
        self.assertEqual(planned_receipt.state, "done")
        self.assertTrue(bill.is_picking_matched)

    def test_32_posting_creates_the_missing_receipt(self):
        """Small shop flow: a bill imported without any purchase order nor
        receipt creates (and validates) its own receipt when posted."""
        self.env.company.auto_create_picking_on_post = True
        self.env.company.auto_validate_matched_picking = True
        bill = self.create_bill([(self.product_b, 8, 100.0)])

        bill.action_post()

        self.assertEqual(bill.state, "posted")
        picking = self.env["stock.picking"].search(
            [("partner_id", "=", self.partner_a.id)]
        )
        self.assertEqual(
            len(picking), 1, "the bill must have generated exactly one receipt"
        )
        self.assertEqual(
            picking.state, "done", "auto_validate_matched_picking applies here too"
        )
        self.assertEqual(picking.move_ids.product_id, self.product_b)
        self.assertEqual(bill.invoice_line_ids.move_line_ids, picking.move_ids)
        self.assertTrue(bill.is_picking_matched)
        # the generated receipt is traceable, and so is the bill
        self.assertIn(bill.name, picking.origin or "")
        self.assertIn("(bill matching)", picking.origin or "")
        self.assertIn(
            "created automatically", " ".join(bill.message_ids.mapped("body"))
        )

    def test_33_posting_creates_nothing_when_the_setting_is_off(self):
        """Default: posting a bill never touches the stock."""
        bill = self.create_bill([(self.product_b, 8, 100.0)])

        bill.action_post()

        self.assertEqual(bill.state, "posted")
        self.assertFalse(
            self.env["stock.picking"].search([("partner_id", "=", self.partner_a.id)])
        )
        self.assertFalse(bill.is_picking_matched)

    def test_34_posting_is_not_blocked_when_the_automation_fails(self):
        """A warehouse failure must not block the accounting validation, and
        the half-done warehouse work must be rolled back."""
        self.env.company.auto_create_picking_on_post = True
        bill = self.create_bill([(self.product_b, 8, 100.0)])

        def _create_then_fail(move):
            # a partial warehouse write, as any failing reception would leave
            self.env["stock.picking"].create(
                {
                    "partner_id": move.partner_id.id,
                    "picking_type_id": self.picking_type_in.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": (
                        self.picking_type_in.default_location_dest_id.id
                    ),
                }
            )
            raise UserError(_("the warehouse is closed"))

        move_model = type(self.env["account.move"])
        with patch.object(
            move_model,
            "_auto_create_picking_for_unmatched_lines",
            new=_create_then_fail,
        ):
            bill.action_post()

        self.assertEqual(bill.state, "posted", "the bill must be posted anyway")
        self.assertFalse(
            self.env["stock.picking"].search([("partner_id", "=", self.partner_a.id)]),
            "the failed reception must have been rolled back",
        )
        self.assertIn(
            "Automatic bill matching failed",
            " ".join(bill.message_ids.mapped("body")),
            "the operator must be told, on the bill, what to do",
        )

    def test_35_posting_creates_nothing_when_a_receipt_can_be_matched(self):
        """The automatic creation only covers the bills with nothing to match:
        as soon as a receipt candidate exists, the operator decides."""
        self.env.company.auto_create_picking_on_post = True
        self.env.company.auto_validate_matched_picking = True
        receipt = self.create_picking([(self.product_a, 8)])
        bill = self.create_bill([(self.product_a, 8, 50.0)])

        bill.action_post()

        self.assertEqual(
            self.env["stock.picking"].search_count(
                [("partner_id", "=", self.partner_a.id)]
            ),
            1,
            "no extra receipt may be created when one exists",
        )
        self.assertEqual(receipt.state, "assigned", "and it is not touched either")
        self.assertFalse(bill.is_picking_matched, "matching stays manual")
