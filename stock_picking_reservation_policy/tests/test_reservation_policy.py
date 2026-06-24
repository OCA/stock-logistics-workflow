# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import ReservationPolicyCommon


class TestReservationPolicy(ReservationPolicyCommon):
    """Reservation policy exercised from operation types and transfers."""

    # -------------------------------------------------------------------------
    # Defaulting
    # -------------------------------------------------------------------------

    def test_picking_defaults_policy_from_operation_type(self):
        """A transfer defaults its reservation policy from its operation type."""
        self.picking_type_out.reservation_policy = "line"
        picking = self._create_picking(qty=5.0)
        self.assertEqual(picking.reservation_policy, "line")

    def test_picking_manual_override(self):
        """The policy can be overridden on the transfer itself."""
        self.picking_type_out.reservation_policy = "direct"
        picking = self._create_picking(qty=5.0, reservation_policy="line")
        self.assertEqual(picking.reservation_policy, "line")

    # -------------------------------------------------------------------------
    # Enforcement at reservation
    # -------------------------------------------------------------------------

    def test_one_insufficient_stock_not_reserved(self):
        """'All or nothing' leaves the move unreserved when stock is short."""
        self._set_stock(5.0)
        picking = self._create_picking(qty=10.0, reservation_policy="line")
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "confirmed")
        self.assertFalse(move.move_line_ids, "Nothing should be reserved")

    def test_one_sufficient_stock_reserved(self):
        """'All or nothing' reserves fully when the whole quantity is available."""
        self._set_stock(10.0)
        picking = self._create_picking(qty=10.0, reservation_policy="line")
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "assigned")
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 10.0)

    def test_direct_partial_reservation(self):
        """'Partial' keeps the standard behavior: reserve what is available."""
        self._set_stock(5.0)
        picking = self._create_picking(qty=10.0, reservation_policy="direct")
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "partially_available")
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 5.0)

    def test_line_policy_does_not_top_up_existing_partial(self):
        """Re-assigning never tops up an existing partial reservation in place.

        Guards against a regression where the policy let core reserve first and
        then discarded the result: core increments a matching move line in place
        before returning, so a partial reservation leaked through despite the
        all-or-nothing policy.

        Scenario:
            1. Start with 5 units and a 'partial' transfer for 10; it reserves 5.
            2. Switch that transfer to 'all or nothing per line'.
            3. Add 3 more units (8 available, still short of 10) and re-assign.
        Expected:
            - The reservation is left untouched at 5 (never topped up to 8).
        """
        self._set_stock(5.0)
        picking = self._create_picking(qty=10.0, reservation_policy="direct")
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "partially_available")
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 5.0)

        picking.reservation_policy = "line"
        self._set_stock(3.0)
        picking.action_assign()
        self.assertEqual(
            sum(move.move_line_ids.mapped("quantity")),
            5.0,
            "An all-or-nothing line must not top up a partial reservation",
        )

    def test_one_skips_free_stock_for_direct_sibling(self):
        """A skipped all-or-nothing line leaves its stock to a 'direct' sibling.

        Scenario:
            - Only 6 units in stock.
            - An 'all or nothing per line' transfer needs 10 (cannot be satisfied).
            - A 'partial' transfer for the same product needs 6.
        Expected:
            - The 'all or nothing' transfer reserves nothing.
            - The 'direct' transfer reserves the full 6 units (the all-or-nothing
              line never grabbed them).
        """
        self._set_stock(6.0)
        p_one = self._create_picking(qty=10.0, reservation_policy="line")
        p_direct = self._create_picking(qty=6.0, reservation_policy="direct")
        pickings = p_one | p_direct
        pickings.action_confirm()
        pickings.action_assign()
        self.assertEqual(p_one.move_ids.state, "confirmed")
        self.assertFalse(p_one.move_ids.move_line_ids)
        self.assertEqual(p_direct.move_ids.state, "assigned")
        self.assertEqual(sum(p_direct.move_ids.move_line_ids.mapped("quantity")), 6.0)

    def test_two_competing_one_moves(self):
        """Two all-or-nothing lines, stock for only one: exactly one is reserved."""
        self._set_stock(10.0)
        p1 = self._create_picking(qty=10.0, reservation_policy="line")
        p2 = self._create_picking(qty=10.0, reservation_policy="line")
        pickings = p1 | p2
        pickings.action_confirm()
        pickings.action_assign()
        states = pickings.move_ids.mapped("state")
        self.assertEqual(
            sorted(states),
            ["assigned", "confirmed"],
            "Exactly one move should be fully reserved, the other left unreserved",
        )

    def test_chained_move_not_affected(self):
        """A chained move (fed by origin moves) keeps the standard behavior.

        The policy must only affect reservation from stock; a move reserving
        from its completed origin moves can still be partially available.
        """
        self.picking_type_out.reservation_policy = "line"
        output_loc = self.warehouse.wh_output_stock_loc_id
        self._set_stock(6.0)  # only 6 available for the pick step

        # Ship step: output -> customer, all-or-nothing operation type.
        ship = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10.0,
                "location_id": output_loc.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        # Pick step: stock -> output, chained to the ship step.
        pick = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10.0,
                "location_id": self.stock_location.id,
                "location_dest_id": output_loc.id,
                "picking_type_id": self.warehouse.pick_type_id.id,
                "move_dest_ids": [Command.link(ship.id)],
            }
        )
        (pick | ship)._action_confirm()
        self.assertEqual(ship.picking_id.reservation_policy, "line")

        # Complete the pick with the 6 available units.
        pick._action_assign()
        self.assertEqual(pick.state, "partially_available")
        for ml in pick.move_line_ids:
            ml.quantity = 6.0
            ml.picked = True
        pick._action_done()

        # The ship move now reserves the 6 units brought by its origin move.
        ship._action_assign()
        self.assertEqual(
            ship.state,
            "partially_available",
            "A chained move must not be subject to the all-or-nothing policy",
        )
        self.assertEqual(sum(ship.move_line_ids.mapped("quantity")), 6.0)
