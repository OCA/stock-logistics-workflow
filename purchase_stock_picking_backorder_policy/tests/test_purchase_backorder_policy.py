# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_picking_backorder_policy.tests.common import (
    BackorderPolicyCommon,
)


class TestPurchaseBackorderPolicy(BackorderPolicyCommon):
    """Backorder policy exercised from vendor configuration and purchase orders."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_in = cls.warehouse.in_type_id
        # Ensure default create_backorder is 'ask'
        cls.picking_type_in.create_backorder = "ask"

    def _create_purchase_order(self, qty=10.0):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.commercial_partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": qty,
                            "price_unit": 1.0,
                        }
                    )
                ],
            }
        )

    def _confirm_and_get_receipt(self, order):
        order.button_confirm()
        self.assertEqual(len(order.picking_ids), 1)
        receipt = order.picking_ids
        receipt.action_assign()
        return receipt

    # -------------------------------------------------------------------------
    # res.partner / purchase.order — purchase_backorder_policy
    # -------------------------------------------------------------------------

    def test_policy_propagates_to_contacts(self):
        """Setting the policy on a company propagates it to its contacts."""
        self.commercial_partner.write({"purchase_backorder_policy": "always"})
        self.assertEqual(
            self.delivery_partner.purchase_backorder_policy,
            "always",
            "Policy set on the commercial entity should sync to its contacts",
        )

    def test_backorder_policy_default_from_vendor(self):
        """An order defaults its backorder policy from the vendor."""
        self.commercial_partner.write({"purchase_backorder_policy": "never"})
        order = self._create_purchase_order()
        self.assertEqual(order.backorder_policy, "never")

    def test_backorder_policy_manual_override_persists(self):
        """A manually chosen policy on the order is preserved.

        Scenario:
            1. An order defaults its policy from the vendor.
            2. A user manually changes the order's policy.
            3. An unrelated field is later edited.
        Expected:
            - The manual choice is kept, since the vendor did not change.
        """
        self.commercial_partner.write({"purchase_backorder_policy": "ask"})
        order = self._create_purchase_order()
        order.write({"backorder_policy": "never"})

        order.write({"partner_ref": "REF-1"})
        self.assertEqual(order.backorder_policy, "never")

    # -------------------------------------------------------------------------
    # purchase.order -> stock.picking propagation
    # -------------------------------------------------------------------------

    def test_receipt_gets_policy_from_order(self):
        """Confirming an order copies its policy onto the receipt and its moves."""
        self.commercial_partner.write({"purchase_backorder_policy": "never"})
        order = self._create_purchase_order()
        receipt = self._confirm_and_get_receipt(order)
        self.assertEqual(receipt.backorder_policy, "never")
        self.assertEqual(receipt.move_ids.backorder_policy, "never")

    def test_receipt_no_policy_falls_back_to_operation_type(self):
        """Without a policy, a partial receipt shows the standard prompt."""
        order = self._create_purchase_order()
        receipt = self._confirm_and_get_receipt(order)
        self.assertFalse(receipt.backorder_policy)
        self._set_qty_done(receipt, 4.0)  # partial

        result = receipt.button_validate()
        self.assertEqual(result.get("res_model"), "stock.backorder.confirmation")
        self.assertNotEqual(receipt.state, "done")

    def test_receipt_policy_always(self):
        """'Always' creates the backorder of the missing quantity automatically.

        Scenario:
            1. The vendor policy is 'Always' (operation default is 'Ask').
            2. Only part of the ordered quantity is received.
        Expected:
            - No prompt is shown and a backorder is created for the rest.
        """
        self.commercial_partner.write({"purchase_backorder_policy": "always"})
        order = self._create_purchase_order()
        receipt = self._confirm_and_get_receipt(order)
        self._set_qty_done(receipt, 6.0)  # partial

        result = receipt.button_validate()
        self.assertIs(result, True, "With 'always' policy, no wizard should be shown")
        self.assertEqual(receipt.state, "done")
        self.assertTrue(receipt.backorder_ids, "A backorder should have been created")

    def test_receipt_policy_never(self):
        """'Never' cancels the missing quantity instead of creating a backorder.

        Scenario:
            1. The vendor policy is 'Never' (operation default is 'Ask').
            2. Only part of the ordered quantity is received.
        Expected:
            - No prompt is shown and no backorder is created.
            - The order is not expecting the missing quantity anymore.
        """
        self.commercial_partner.write({"purchase_backorder_policy": "never"})
        order = self._create_purchase_order()
        receipt = self._confirm_and_get_receipt(order)
        self._set_qty_done(receipt, 6.0)  # partial

        result = receipt.button_validate()
        self.assertIs(result, True, "With 'never' policy, no wizard should be shown")
        self.assertEqual(receipt.state, "done")
        self.assertFalse(receipt.backorder_ids, "No backorder should be created")
        self.assertEqual(order.order_line.qty_received, 6.0)
