# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2022 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .common import TestProcurementGroupCarrierCommon


@tagged("post_install", "-at_install")
class TestProcurementGroupCarrier(TestProcurementGroupCarrierCommon):
    def _set_pickship(self, order, propagate_carrier):
        order.warehouse_id.delivery_steps = "pick_ship"
        delivery_route = order.warehouse_id.delivery_route_id
        pick_rule, ship_rule = delivery_route.rule_ids
        ship_rule.propagate_carrier = True
        ship_rule.write({"action": "pull"})
        pick_rule.location_dest_id = delivery_route.rule_ids[1].location_src_id
        pick_rule.propagate_carrier = propagate_carrier

    def test_sale_procurement_group_carrier(self):
        """Check the SO procurement group contains the carrier on SO confirmation"""
        order = self._create_sale_order([(self.product, 1.0)], carrier=self.carrier)
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        self.assertEqual(order.procurement_group_id.carrier_id, order.carrier_id)

    def test_sale_picking_group_carrier_aligned_with_propagate(self):
        """Check picking carrier is set from procurement group"""
        # Create an order without carrier but set carrier on proc group
        order = self._create_sale_order([(self.product, 1.0)])
        group_vals = order.order_line._prepare_procurement_group_vals()
        group_vals["carrier_id"] = self.carrier.id
        order.procurement_group_id = self.env["procurement.group"].create(group_vals)
        self._set_pickship(order, propagate_carrier=True)
        order.action_confirm()
        out_transfer = order.picking_ids.filtered(
            lambda pick: pick.location_dest_id.usage == "customer"
        )
        pick_transfer = order.picking_ids - out_transfer
        move_group = order.procurement_group_id
        self.assertFalse(order.carrier_id)
        self.assertEqual(out_transfer.carrier_id, self.carrier)
        self.assertEqual(move_group.carrier_id, self.carrier)
        self.assertEqual(pick_transfer.carrier_id, self.carrier)

    def test_sale_picking_group_carrier_aligned_without_propagate(self):
        """Check picking carrier is set from procurement group

        And check changing the carrier keeps the group aligned"""
        # Create an order without carrier but set carrier on proc group
        order = self._create_sale_order([(self.product, 1.0)])
        group_vals = order.order_line._prepare_procurement_group_vals()
        group_vals["carrier_id"] = self.carrier.id
        order.procurement_group_id = self.env["procurement.group"].create(group_vals)
        self._set_pickship(order, propagate_carrier=False)
        order.action_confirm()
        out_transfer = order.picking_ids.filtered(
            lambda pick: pick.location_dest_id.usage == "customer"
        )
        pick_transfer = order.picking_ids - out_transfer
        move_group = order.procurement_group_id
        self.assertFalse(order.carrier_id)
        self.assertEqual(out_transfer.carrier_id, self.carrier)
        self.assertEqual(move_group.carrier_id, self.carrier)
        self.assertFalse(pick_transfer.carrier_id)

        # Change the carrier on the out transfer
        # Carrier on group needs to be changed
        # but not on the pick transfer
        out_transfer.carrier_id = self.carrier2
        self.assertEqual(move_group.carrier_id, self.carrier2)
        self.assertFalse(pick_transfer.carrier_id)

        # Now change carrier on order (odoo allows it)
        # In odoo standard all pickings and order references the new carrier
        self._add_carrier_to_order(order, self.carrier3)
        move_group = order.procurement_group_id
        self.assertEqual(order.carrier_id, self.carrier3)
        self.assertEqual(out_transfer.carrier_id, self.carrier3)
        self.assertEqual(pick_transfer.carrier_id, self.carrier3)
        self.assertEqual(move_group.carrier_id, self.carrier3)

        # Now since the carrier is set on out and pick tranfer
        # updating the carrier on the out transfer
        # should also change the carrier on the pick transfer
        out_transfer.carrier_id = self.carrier
        self.assertEqual(out_transfer.carrier_id, self.carrier)
        self.assertEqual(pick_transfer.carrier_id, self.carrier)
        self.assertEqual(move_group.carrier_id, self.carrier)

        # Ensure carrier can be set to False
        out_transfer.carrier_id = False
        self.assertFalse(out_transfer.carrier_id)
        self.assertFalse(pick_transfer.carrier_id)
        self.assertFalse(move_group.carrier_id)
