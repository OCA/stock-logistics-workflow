# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestTwoStepReceipt(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.reception_steps = "two_steps"
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.input_location = cls.warehouse.wh_input_stock_loc_id
        # Valuation on the input location too, so the perpetual entry is
        # generated for the supplier -> input move.
        cls.input_location.valuation_account_id = (
            cls.stock_location.valuation_account_id
        )
        cls.product = cls.products[0]

    def _create_receipt(self, qty):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.warehouse.in_type_id
        with picking_form.move_ids.new() as move:
            move.product_id = self.product
            move.product_uom_qty = qty
        picking = picking_form.save()
        return picking

    def test_two_step_receipt_backdating(self):
        date_backdating = self._get_datetime_backdating(5)
        receipt = self._create_receipt(3)
        receipt.action_confirm()
        receipt.action_assign()
        for move in receipt.move_ids:
            move.quantity = move.product_uom_qty
        self._create_wizard(date_backdating, receipt)
        receipt.button_validate()
        self.assertEqual(receipt.state, "done")
        self.assertEqual(receipt.move_ids.date.date(), date_backdating.date())

        # The two-step config chained an internal transfer input -> stock,
        # linked through move_dest_ids.
        internal = receipt.move_ids.move_dest_ids.picking_id
        self.assertTrue(internal, "Two-step receipt should chain an internal move")
        internal.action_assign()
        for move in internal.move_ids:
            move.quantity = move.product_uom_qty
        self._create_wizard(date_backdating, internal)
        internal.button_validate()
        self.assertEqual(internal.state, "done")
        self.assertEqual(internal.move_ids.date.date(), date_backdating.date())

    def test_two_step_receipt_backorder_backdating(self):
        """Partial two-step receipt that generates a backorder, backdated."""
        date_backdating = self._get_datetime_backdating(5)
        receipt = self._create_receipt(3)
        receipt.action_confirm()
        receipt.action_assign()
        # Receive only 2 of 3 -> backorder.
        for move in receipt.move_ids:
            move.move_line_ids[:1].quantity = 2
        self._create_wizard(date_backdating, receipt)
        res = receipt.button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            wizard = Form(
                self.env[res["res_model"]].with_context(**res["context"])
            ).save()
            wizard.process()
        self.assertEqual(receipt.state, "done")
        self.assertEqual(receipt.move_ids.date.date(), date_backdating.date())

    def test_two_step_only_internal_backdated(self):
        """Receipt processed today; only the internal transfer is backdated."""
        date_backdating = self._get_datetime_backdating(5)
        receipt = self._create_receipt(3)
        receipt.action_confirm()
        receipt.action_assign()
        for move in receipt.move_ids:
            move.quantity = move.product_uom_qty
        receipt.button_validate()
        self.assertEqual(receipt.state, "done")
        internal = receipt.move_ids.move_dest_ids.picking_id
        self.assertTrue(internal)
        internal.action_assign()
        for move in internal.move_ids:
            move.quantity = move.product_uom_qty
        self._create_wizard(date_backdating, internal)
        internal.button_validate()
        self.assertEqual(internal.state, "done")
        self.assertEqual(internal.move_ids.date.date(), date_backdating.date())

    def _create_purchase_order(self, qty, price_unit):
        partner = self.env["res.partner"].create({"name": "Two-step Vendor"})
        return self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": qty,
                            "product_uom_id": self.product.uom_id.id,
                            "price_unit": price_unit,
                            "name": self.product.name,
                        },
                    ),
                ],
            }
        )

    def test_two_step_purchase_receipt_backdating(self):
        """Backdate a two-step receipt coming from a purchase order.

        This exercises the ``stock.move._get_price_unit`` override (which is
        only reached for moves with a ``purchase_line_id`` while a
        ``date_backdating`` context is active) together with the chained
        input -> stock internal transfer.
        """
        if "purchase.order" not in self.env:
            self.skipTest("purchase not installed")  # pragma: no cover
        date_backdating = self._get_datetime_backdating(5)
        po = self._create_purchase_order(3, 50)
        po.button_confirm()
        receipt = po.picking_ids
        self.assertEqual(len(receipt), 1)
        receipt.action_assign()
        for move in receipt.move_ids:
            move.quantity = move.product_uom_qty
        self._create_wizard(date_backdating, receipt)
        receipt.button_validate()
        self.assertEqual(receipt.state, "done")
        self.assertEqual(receipt.move_ids.date.date(), date_backdating.date())

        internal = receipt.move_ids.move_dest_ids.picking_id
        self.assertTrue(internal, "Two-step receipt should chain an internal move")
        internal.action_assign()
        for move in internal.move_ids:
            move.quantity = move.product_uom_qty
        self._create_wizard(date_backdating, internal)
        internal.button_validate()
        self.assertEqual(internal.state, "done")
        self.assertEqual(internal.move_ids.date.date(), date_backdating.date())
