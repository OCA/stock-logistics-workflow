# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2022 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .common import TestProcurementGroupCarrierCommon


@tagged("post_install", "-at_install")
class TestProcurementGroupCarrier(TestProcurementGroupCarrierCommon):
    def test_sale_procurement_group_carrier(self):
        """Check the SO procurement group contains the carrier on SO confirmation"""
        order = self._create_sale_order([(self.product, 1.0)], carrier=self.carrier)
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        self.assertEqual(order.procurement_group_id.carrier_id, order.carrier_id)

    def test_sale_picking_group_carrier_aligned(self):
        # Create an order without carrier
        order = self._create_sale_order([(self.product, 1.0)])
        order.warehouse_id.delivery_steps = "pick_ship"
        order.warehouse_id.delivery_route_id.rule_ids.propagate_carrier = False
        order.carrier_id = self.carrier
        order.action_confirm()
        out_transfer = order.picking_ids.filtered(
            lambda pick: pick.location_dest_id.usage == "customer"
        )
        pick_transfer = order.picking_ids - out_transfer
        move_group = order.procurement_group_id
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
