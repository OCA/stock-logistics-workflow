# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleReservationPolicy(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.quick_ref("uom.product_uom_unit").id,
            }
        )
        cls.warehouse = cls.quick_ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.quick_ref("stock.stock_location_customers")
        cls.commercial_partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "is_company": True}
        )
        cls.delivery_partner = cls.env["res.partner"].create(
            {
                "name": "Test Delivery Address",
                "parent_id": cls.commercial_partner.id,
                "type": "delivery",
            }
        )

    @classmethod
    def _set_stock(cls, qty):
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, qty
        )

    def _create_sale_order(self, partner, qty=5.0):
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": qty}
                    )
                ],
            }
        )

    # -------------------------------------------------------------------------
    # Partner / sale order fields
    # -------------------------------------------------------------------------

    def test_partner_policy_propagates_to_contacts(self):
        """Setting the policy on a company propagates it to its contacts."""
        self.commercial_partner.reservation_policy = "line"
        self.assertEqual(self.delivery_partner.reservation_policy, "line")

    def test_order_defaults_from_partner(self):
        """An order defaults its reservation policy from the customer."""
        self.commercial_partner.reservation_policy = "line"
        order = self._create_sale_order(self.commercial_partner)
        self.assertEqual(order.reservation_policy, "line")

    def test_order_default_is_direct(self):
        """Without a partner preference, the order defaults to 'direct'."""
        order = self._create_sale_order(self.commercial_partner)
        self.assertEqual(order.reservation_policy, "direct")

    def test_order_recomputes_on_partner_change(self):
        """Changing the customer recomputes the order's policy."""
        self.commercial_partner.reservation_policy = "line"
        partner2 = self.env["res.partner"].create(
            {"name": "Partner 2", "reservation_policy": "direct"}
        )
        order = self._create_sale_order(self.commercial_partner)
        self.assertEqual(order.reservation_policy, "line")
        order.partner_id = partner2
        self.assertEqual(order.reservation_policy, "direct")

    # -------------------------------------------------------------------------
    # sale.order -> stock.picking propagation
    # -------------------------------------------------------------------------

    def test_picking_gets_policy_from_order(self):
        """Confirming an order copies its policy onto the delivery."""
        self.commercial_partner.reservation_policy = "line"
        self._set_stock(100.0)
        order = self._create_sale_order(self.commercial_partner)
        self.assertEqual(order.reservation_policy, "line")
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        for picking in order.picking_ids:
            self.assertEqual(picking.reservation_policy, "line")

    def test_picking_keeps_order_override_over_partner_default(self):
        """The order's policy wins over the operation type default on delivery."""
        self.commercial_partner.reservation_policy = "direct"
        self._set_stock(100.0)
        order = self._create_sale_order(self.commercial_partner)
        order.reservation_policy = "line"
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        for picking in order.picking_ids:
            self.assertEqual(picking.reservation_policy, "line")

    def test_one_order_insufficient_stock_not_reserved(self):
        """An 'all or nothing' order leaves the delivery unreserved when short."""
        self.commercial_partner.reservation_policy = "line"
        self._set_stock(3.0)  # less than ordered
        order = self._create_sale_order(self.commercial_partner, qty=10.0)
        order.action_confirm()
        picking = order.picking_ids
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "confirmed")
        self.assertFalse(move.move_line_ids, "Nothing should be reserved")

    def test_direct_order_partial_reservation(self):
        """A 'partial' order keeps the standard partial reservation behavior."""
        self.commercial_partner.reservation_policy = "direct"
        self._set_stock(3.0)
        order = self._create_sale_order(self.commercial_partner, qty=10.0)
        order.action_confirm()
        picking = order.picking_ids
        picking.action_assign()
        move = picking.move_ids
        self.assertEqual(move.state, "partially_available")
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 3.0)

    # -------------------------------------------------------------------------
    # A transfer never mixes reservation policies
    # -------------------------------------------------------------------------

    def test_moves_with_different_policy_split_pickings(self):
        """Moves whose sale orders use different policies don't share a transfer.

        Two moves with otherwise-identical picking-assignation keys but linked to
        sale orders with different reservation policies must land in separate
        transfers, each carrying its own policy.
        """
        so_line = self._create_sale_order(self.commercial_partner)
        so_line.reservation_policy = "line"
        so_direct = self._create_sale_order(self.commercial_partner)
        so_direct.reservation_policy = "direct"
        move_vals = {
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
            "picking_type_id": self.warehouse.out_type_id.id,
            "location_id": self.stock_location.id,
            "location_dest_id": self.customer_location.id,
        }
        move_line = self.env["stock.move"].create(
            {**move_vals, "sale_line_id": so_line.order_line.id}
        )
        move_direct = self.env["stock.move"].create(
            {**move_vals, "sale_line_id": so_direct.order_line.id}
        )
        (move_line | move_direct)._action_confirm()
        self.assertTrue(move_line.picking_id)
        self.assertNotEqual(
            move_line.picking_id,
            move_direct.picking_id,
            "Moves of different reservation policy must not share a transfer",
        )
        self.assertEqual(move_line.picking_id.reservation_policy, "line")
        self.assertEqual(move_direct.picking_id.reservation_policy, "direct")
