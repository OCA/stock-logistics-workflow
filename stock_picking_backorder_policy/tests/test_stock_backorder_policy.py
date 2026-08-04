# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from .common import BackorderPolicyCommon


class TestStockBackorderPolicy(BackorderPolicyCommon):
    """Backorder policy exercised from pickings/moves created directly.

    These tests drive the policy from the picking or its moves, without
    involving a sale order.
    """

    def _create_picking(self, qty=10.0, backorder_policy=False):
        """Helper: create a confirmed, reserved outgoing picking."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "partner_id": self.commercial_partner.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        if backorder_policy:
            picking.backorder_policy = backorder_policy
        picking.action_confirm()
        picking.action_assign()
        return picking

    def _assertIsBackorderWizard(self, result):
        """Assert ``button_validate`` returned the backorder confirmation wizard."""
        self.assertIsInstance(
            result, dict, "Expected button_validate to return a wizard action"
        )
        self.assertEqual(result.get("res_model"), "stock.backorder.confirmation")

    def test_no_policy_falls_back_to_operation_type(self):
        """Without a policy on the delivery, the standard backorder prompt applies.

        Scenario:
            1. The delivery has no backorder policy.
            2. It is partially done.
        Expected:
            - The usual backorder prompt is triggered, as in standard Odoo.
        """
        picking = self._create_picking(qty=10.0)
        self._set_qty_done(picking, 5.0)  # partial
        result = picking.button_validate()
        self._assertIsBackorderWizard(result)
        # The picking is not validated until the wizard is confirmed.
        self.assertNotEqual(picking.state, "done")

    def test_policy_always(self):
        """'Always' creates the backorder automatically and logs it.

        Scenario:
            1. The delivery's policy is 'Always' (operation default is 'Ask').
            2. It is partially done.
        Expected:
            - No backorder prompt is shown.
            - A backorder is created automatically.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="always")
        self._set_qty_done(picking, 6.0)  # partial

        # Validation goes through without prompting and creates a backorder.
        result = picking.button_validate()
        self.assertIs(result, True, "With 'always' policy, no wizard should be shown")
        self.assertEqual(picking.state, "done")
        self.assertTrue(
            picking.backorder_ids, "A backorder should have been auto-created"
        )

    def test_policy_never(self):
        """'Never' cancels the remaining demand instead of creating a backorder.

        Scenario:
            1. The delivery's policy is 'Never' (operation default is 'Ask').
            2. It is partially done.
        Expected:
            - No backorder prompt is shown.
            - No backorder is created; the unfulfilled demand is cancelled.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="never")
        self._set_qty_done(picking, 4.0)  # partial

        result = picking.button_validate()
        self.assertIs(result, True, "With 'never' policy, no wizard should be shown")
        self.assertEqual(picking.state, "done")
        self.assertFalse(
            picking.backorder_ids,
            "No backorder should have been created for 'never' policy",
        )

    def test_policy_not_enforced_outside_button_validate(self):
        """The policy only governs the interactive validation action.

        A programmatic ``_action_done()`` (e.g. POS, marketplace auto-fulfill,
        rental pickup, scrap, inventory) bypasses ``button_validate`` and is not
        tagged with ``button_validate_picking_ids``, so the policy must not kick
        in — the standard behavior (here, a backorder is created) is preserved.

        This is the counterpart of :meth:`test_policy_never`, which exercises
        the same picking through ``button_validate``.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="never")
        self._set_qty_done(picking, 4.0)  # partial

        # Low-level validation, as an automated flow would do it.
        picking._action_done()

        self.assertEqual(picking.state, "done")
        self.assertTrue(
            picking.backorder_ids,
            "Outside button_validate the 'never' policy must not be enforced; "
            "the standard backorder should still be created",
        )

    def test_policy_ask(self):
        """'Ask' behaves exactly like the standard backorder prompt."""
        picking = self._create_picking(qty=10.0, backorder_policy="ask")
        self._set_qty_done(picking, 5.0)

        result = picking.button_validate()
        self._assertIsBackorderWizard(result)
        self.assertNotEqual(picking.state, "done")

    def test_full_delivery_no_backorder_check(self):
        """A fully delivered transfer triggers no backorder handling.

        Scenario:
            1. The delivery's policy is 'Always'.
            2. The delivery is completed in full.
        Expected:
            - No backorder is created (there is nothing left to backorder).
        """
        picking = self._create_picking(qty=5.0, backorder_policy="always")
        self._set_qty_done(picking, 5.0)  # full delivery

        result = picking.button_validate()
        self.assertIs(result, True)
        self.assertEqual(picking.state, "done")
        self.assertFalse(
            picking.backorder_ids, "No backorder expected for full delivery"
        )

    def test_moves_with_different_policy_split_pickings(self):
        """Operations with different policies are kept apart.

        Scenario:
            1. Two otherwise-identical deliveries have different policies.
        Expected:
            - They are not merged and land in separate transfers, each keeping
              its own policy.
        """
        move_vals = {
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
            "picking_type_id": self.picking_type_out.id,
            "location_id": self.stock_location.id,
            "location_dest_id": self.customer_location.id,
        }
        move_always = self.env["stock.move"].create(
            {**move_vals, "backorder_policy": "always"}
        )
        move_never = self.env["stock.move"].create(
            {**move_vals, "backorder_policy": "never"}
        )
        moves = move_always | move_never
        moves._action_confirm()

        # Not merged (still two distinct moves)...
        self.assertEqual(len(moves.exists()), 2)
        # ...and assigned to two different pickings, each with its own policy.
        self.assertTrue(move_always.picking_id)
        self.assertNotEqual(move_always.picking_id, move_never.picking_id)
        self.assertEqual(move_always.picking_id.backorder_policy, "always")
        self.assertEqual(move_never.picking_id.backorder_policy, "never")

    def test_policy_propagates_through_mto_chain(self):
        """The policy follows a make-to-order (pull) procurement chain.

        Scenario:
            1. A two-step delivery (pick + ship) is procured on order (MTO), so
               confirming the outgoing move runs procurement and creates the
               chained upstream (pick) move via a pull rule.
        Expected:
            - The chained move carries the originating move's policy
              (propagated through ``_prepare_procurement_values``).
        """
        self.warehouse.write({"delivery_steps": "pick_ship"})
        output_loc = self.warehouse.wh_output_stock_loc_id
        # A pull rule that replenishes the output location from stock, so
        # confirming the (make-to-order) outgoing move generates the chained
        # upstream (pick) move via procurement. The generated move itself is
        # make-to-stock, so the chain terminates at stock (no further rule
        # needed, e.g. purchase replenishment of WH/Stock).
        route = self.env["stock.route"].create(
            {
                "name": "Test MTO output replenishment",
                "product_selectable": True,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Stock -> Output",
                            "action": "pull",
                            "procure_method": "make_to_stock",
                            "location_src_id": self.stock_location.id,
                            "location_dest_id": output_loc.id,
                            "picking_type_id": self.warehouse.pick_type_id.id,
                        }
                    )
                ],
            }
        )
        self.product.route_ids = [Command.set(route.ids)]

        # Outgoing move (output -> customer), procured on order: confirming it
        # triggers the pull rule that generates the upstream pick move.
        ship_move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 5.0,
                "location_id": output_loc.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
                "procure_method": "make_to_order",
                "backorder_policy": "never",
            }
        )
        ship_move._action_confirm()

        upstream = ship_move.move_orig_ids
        self.assertTrue(
            upstream, "A chained (pick) move should have been procured on order"
        )
        self.assertEqual(
            upstream.backorder_policy,
            "never",
            "The policy must propagate through the MTO procurement chain",
        )

    def test_return_ignores_policy_always(self):
        """Test the delivery's 'Always' policy is ignored when processing a return.

        Scenario:
            1. A delivery with an 'Always' backorder policy is fully processed,
               then a return is created for part of the quantity.
            2. Only part of the return quantity is processed.
        Expected:
            - The standard backorder prompt is shown for the return (as if
              there was no policy), instead of auto-creating a backorder.
            - The return still carries the 'Always' policy inherited from the
              delivery: the fix bypasses enforcement, it does not clear the
              field.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="always")
        self._set_qty_done(picking, 10.0)  # full delivery
        picking.button_validate()

        return_picking = self._create_return(picking, quantity=4.0)
        self.assertEqual(return_picking.backorder_policy, "always")
        self._set_qty_done(return_picking, 2.0)  # partial

        result = return_picking.button_validate()
        self._assertIsBackorderWizard(result)
        self.assertNotEqual(return_picking.state, "done")

    def test_return_ignores_policy_never(self):
        """Test the delivery's 'Never' policy is ignored when processing a return.

        Scenario: as :meth:`test_return_ignores_policy_always`, but with a
        'Never' policy.
        Expected:
            - The standard backorder prompt is shown for the return, instead
              of silently cancelling the remaining demand.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="never")
        self._set_qty_done(picking, 10.0)  # full delivery
        picking.button_validate()

        return_picking = self._create_return(picking, quantity=4.0)
        self.assertEqual(return_picking.backorder_policy, "never")
        self._set_qty_done(return_picking, 2.0)  # partial

        result = return_picking.button_validate()
        self._assertIsBackorderWizard(result)
        self.assertNotEqual(return_picking.state, "done")

    def test_return_no_backorder_when_declined(self):
        """Test declining the backorder wizard on a return creates no backorder.

        Scenario:
            1. A delivery has an 'Always' backorder policy.
            2. A return is partially processed, triggering the standard
               backorder prompt (see :meth:`test_return_ignores_policy_always`).
            3. The prompt is answered with 'No Backorder'.
        Expected:
            - The return is validated and no backorder is created, exactly
              like a standard return without any policy.
        """
        picking = self._create_picking(qty=10.0, backorder_policy="always")
        self._set_qty_done(picking, 10.0)  # full delivery
        picking.button_validate()

        return_picking = self._create_return(picking, quantity=4.0)
        self._set_qty_done(return_picking, 2.0)  # partial

        result = return_picking.button_validate()
        backorder_wizard = Form(
            self.env["stock.backorder.confirmation"].with_context(**result["context"])
        ).save()
        backorder_wizard.process_cancel_backorder()

        self.assertEqual(return_picking.state, "done")
        self.assertFalse(
            return_picking.backorder_ids,
            "No backorder should have been created after declining the wizard",
        )
