# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_picking_backorder_policy.tests.common import (
    BackorderPolicyCommon,
)


class TestSaleBackorderPolicy(BackorderPolicyCommon):
    """Backorder policy exercised from partner configuration and sale orders."""

    def _create_sale_order(self, partner, qty=5.0):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                        }
                    )
                ],
            }
        )

    # -------------------------------------------------------------------------
    # res.partner — sale_backorder_policy
    # -------------------------------------------------------------------------

    def test_policy_propagates_to_contacts(self):
        """Setting the policy on a company propagates it to its contacts."""
        self.commercial_partner.write({"sale_backorder_policy": "always"})
        self.assertEqual(
            self.delivery_partner.sale_backorder_policy,
            "always",
            "Policy set on the commercial entity should sync to its contacts",
        )

    # -------------------------------------------------------------------------
    # sale.order — backorder_policy (computed, stored, writeable)
    # -------------------------------------------------------------------------

    def test_backorder_policy_no_partner_policy(self):
        """An order for a customer with no policy has no backorder policy."""
        self.commercial_partner.write({"sale_backorder_policy": False})
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
            }
        )
        self.assertFalse(order.backorder_policy)

    def test_backorder_policy_default_from_partner(self):
        """An order defaults its backorder policy from the customer."""
        self.commercial_partner.write({"sale_backorder_policy": "never"})
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
            }
        )
        self.assertEqual(order.backorder_policy, "never")

    def test_backorder_policy_delivery_address_wins(self):
        """An order takes its policy from the delivery address, not the company."""
        self.commercial_partner.write({"sale_backorder_policy": "never"})
        self.delivery_partner.write({"sale_backorder_policy": "always"})
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
                "partner_shipping_id": self.delivery_partner.id,
            }
        )
        self.assertEqual(order.backorder_policy, "always")

    def test_backorder_policy_recomputes_on_partner_change(self):
        """Changing the order's customer recomputes its backorder policy."""
        self.commercial_partner.write({"sale_backorder_policy": "ask"})
        partner2 = self.env["res.partner"].create(
            {
                "name": "Partner 2",
                "sale_backorder_policy": "never",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
            }
        )
        self.assertEqual(order.backorder_policy, "ask")

        order.write({"partner_id": partner2.id})
        self.assertEqual(order.backorder_policy, "never")

    def test_backorder_policy_manual_override_persists(self):
        """A manually chosen policy on the order is preserved.

        Scenario:
            1. An order defaults its policy from the customer.
            2. A user manually changes the order's policy.
            3. An unrelated field is later edited.
        Expected:
            - The manual choice is kept, since the customer did not change.
        """
        self.commercial_partner.write({"sale_backorder_policy": "ask"})
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
            }
        )
        self.assertEqual(order.backorder_policy, "ask")

        order.write({"backorder_policy": "never"})
        self.assertEqual(
            order.backorder_policy,
            "never",
            "Manual override must persist when partner is unchanged",
        )

        # Unrelated write must not reset the manual value.
        order.write({"client_order_ref": "REF-1"})
        self.assertEqual(order.backorder_policy, "never")

    def test_backorder_policy_override_reset_on_partner_change(self):
        """Changing the customer overrides a manual policy choice.

        Scenario:
            1. A user manually sets the order's policy.
            2. The order's customer is then changed.
        Expected:
            - The policy is recomputed from the new customer.
        """
        self.commercial_partner.write({"sale_backorder_policy": "ask"})
        partner2 = self.env["res.partner"].create(
            {
                "name": "Partner 2",
                "sale_backorder_policy": "always",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
            }
        )
        order.write({"backorder_policy": "never"})
        self.assertEqual(order.backorder_policy, "never")

        order.write({"partner_id": partner2.id})
        self.assertEqual(
            order.backorder_policy,
            "always",
            "Changing the customer must recompute the policy",
        )

    # -------------------------------------------------------------------------
    # sale.order -> stock.picking propagation
    # -------------------------------------------------------------------------

    def test_picking_gets_policy_from_order(self):
        """Confirming an order copies its policy onto the delivery."""
        self.commercial_partner.write({"sale_backorder_policy": "never"})
        order = self._create_sale_order(self.commercial_partner)
        self.assertEqual(order.backorder_policy, "never")
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        for picking in order.picking_ids:
            self.assertEqual(picking.backorder_policy, "never")

    def test_picking_keeps_order_override_over_customer_policy(self):
        """A manual policy on the order wins over the customer's own.

        Scenario:
            1. The customer's policy is 'Always'.
            2. The order's policy is manually overridden to 'Never'.
        Expected:
            - The delivery carries 'Never', the value set on the order.
        """
        self.commercial_partner.write({"sale_backorder_policy": "always"})
        order = self._create_sale_order(self.commercial_partner)
        order.backorder_policy = "never"
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        for picking in order.picking_ids:
            self.assertEqual(picking.backorder_policy, "never")

    def test_picking_policy_with_chained_operations(self):
        """The policy follows a two-step (pick + ship) delivery.

        Scenario:
            1. The warehouse delivers in two steps; the customer policy is 'Always'.
            2. The order is confirmed and the first step (pick) is completed.
        Expected:
            - The pick carries the policy.
            - The chained ship step, created afterwards, also carries it.
        """
        self.warehouse.write({"delivery_steps": "pick_ship"})
        self.commercial_partner.write({"sale_backorder_policy": "always"})
        order = self._create_sale_order(self.commercial_partner)
        order.action_confirm()

        # At confirmation only the Pick step exists; it already carries the policy.
        pick = order.picking_ids
        self.assertEqual(len(pick), 1)
        self.assertEqual(pick.backorder_policy, "always")

        # Completing the Pick triggers the chained Ship step (push rule).
        pick.action_assign()
        self._set_qty_done(pick, 5.0)
        pick.button_validate()

        ship = order.picking_ids - pick
        self.assertEqual(len(ship), 1, "Chained Ship picking should have been created")
        self.assertEqual(
            ship.backorder_policy,
            "always",
            "Policy must survive the chained (push) ship step",
        )

    def _complete_chain_step(self, picking, qty):
        """Reserve and fully process the available quantity on one chain step."""
        picking.action_assign()
        self.assertIn(
            picking.state,
            ("assigned", "partially_available"),
            "The chain step should be ready to process",
        )
        self.assertEqual(
            picking.backorder_policy,
            "never",
            "The policy must propagate to every step of the chain",
        )
        self._set_qty_done(picking, qty)
        picking.button_validate()

    def test_pick_pack_ship_never_no_dangling_backorders(self):
        """'Never' drops the shortage cleanly across a 3-step delivery.

        Scenario:
            1. The warehouse delivers in three steps (pick + pack + ship).
            2. The customer policy is 'Never' and stock is short (6 of 10 ordered).
            3. Each step is validated for the available quantity in turn.
        Expected:
            - The policy reaches every step of the chain.
            - 6 units reach the customer, the missing 4 are dropped.
            - No backorder is left anywhere in the chain.
        """
        self.warehouse.write({"delivery_steps": "pick_pack_ship"})
        self.commercial_partner.write({"sale_backorder_policy": "never"})
        # Dedicated product with a controlled shortage (6 available, 10 ordered).
        product = self.env["product.product"].create(
            {
                "name": "Shortage Product",
                "type": "consu",
                "is_storable": True,
                "uom_id": self.quick_ref("uom.product_uom_unit").id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 6.0
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.commercial_partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 10.0,
                        }
                    )
                ],
            }
        )
        order.action_confirm()

        # The chain is push-based: only the pick exists at confirmation, and
        # each completed step reveals the next one. Process the three known
        # steps explicitly so a missing or unexpected step fails loudly.
        self.assertEqual(
            len(order.picking_ids), 1, "Only the pick should exist at confirmation"
        )
        pick = order.picking_ids
        self.assertEqual(pick.picking_type_id, self.warehouse.pick_type_id)
        self._complete_chain_step(pick, 6.0)

        pack = order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.pack_type_id
        )
        self.assertEqual(len(pack), 1, "The pack step should appear after the pick")
        self._complete_chain_step(pack, 6.0)

        ship = order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.out_type_id
        )
        self.assertEqual(len(ship), 1, "The ship step should appear after the pack")
        self._complete_chain_step(ship, 6.0)

        # The whole chain is resolved with no dangling transfers or backorders.
        self.assertEqual(len(order.picking_ids), 3, "Exactly pick + pack + ship")
        self.assertFalse(
            order.picking_ids.filtered(lambda p: p.state != "done"),
            "Every transfer should be done",
        )
        self.assertFalse(
            order.picking_ids.filtered(lambda p: p.backorder_id),
            "No backorder should have been created under the 'never' policy",
        )
        # Exactly the available 6 units reached the customer.
        delivered = order.picking_ids.move_ids.filtered(
            lambda m: m.state == "done" and m.location_dest_id == self.customer_location
        )
        self.assertEqual(sum(delivered.mapped("quantity")), 6.0)
