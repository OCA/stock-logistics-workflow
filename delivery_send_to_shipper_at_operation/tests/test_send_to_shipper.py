# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import mock

from odoo.tests.common import SavepointCase


class TestDeliverySendToShipper(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.delivery_steps = "pick_pack_ship"
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        # cls.pack_location = cls.wh.wh_pack_stock_loc_id
        cls.ship_location = cls.wh.wh_output_stock_loc_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        # put product in stock
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 10.0,
        )
        # create carriers
        delivery_fee = cls.env.ref("delivery.product_product_delivery")
        cls.carrier_on_ship = cls.env["delivery.carrier"].create(
            {
                "name": "Carrier On Ship",
                "product_id": delivery_fee.id,
                "integration_level": "rate_and_ship",
                "send_delivery_notice_on": "ship",
            }
        )
        cls.carrier_on_pack = cls.env["delivery.carrier"].create(
            {
                "name": "Carrier On Pack",
                "product_id": delivery_fee.id,
                "integration_level": "rate_and_ship",
                "send_delivery_notice_on": "custom",
                "send_delivery_notice_picking_type_ids": [
                    (6, 0, cls.wh.pack_type_id.ids)
                ],
            }
        )
        # create a pick/pack/ship transfer
        cls.ship_move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "product_id": cls.product.id,
                "product_uom_qty": 10.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.ship_location.id,
                "location_dest_id": cls.customer_location.id,
                "warehouse_id": cls.wh.id,
                "picking_type_id": cls.wh.out_type_id.id,
                "procure_method": "make_to_order",
                "state": "draft",
            }
        )
        cls.ship_move._assign_picking()
        cls.ship_move._action_confirm()
        cls.pack_move = cls.ship_move.move_orig_ids[0]
        cls.pick_move = cls.pack_move.move_orig_ids[0]
        cls.picking = cls.pick_move.picking_id
        cls.packing = cls.pack_move.picking_id
        cls.shipping = cls.ship_move.picking_id
        cls.picking.action_assign()

    def _validate_picking(self, picking):
        for ml in picking.move_line_ids:
            ml.qty_done = ml.product_uom_qty
        picking.action_done()

    def test_send_to_shipper_on_ship(self):
        """Check sending of delivery notification on ship.

        No delivery notification is sent to the carrier when the pack is
        validated (std Odoo behavior).
        """
        self.shipping.carrier_id = self.carrier_on_ship
        self._validate_picking(self.picking)
        self.assertEqual(self.picking.state, "done")
        # Validate the pack: delivery notification is not sent
        with mock.patch.object(type(self.packing), "send_to_shipper") as mocked:
            self._validate_picking(self.packing)
            self.assertEqual(self.packing.state, "done")
            mocked.assert_not_called()
            self.assertFalse(self.shipping.delivery_notification_sent)
        # Validate the ship: delivery notification is sent
        with mock.patch.object(
            type(self.shipping.carrier_id), "send_shipping"
        ) as mocked:
            self._validate_picking(self.shipping)
            self.assertEqual(self.shipping.state, "done")
            mocked.assert_called()
            self.assertFalse(self.shipping.delivery_notification_sent)

    def test_send_to_shipper_on_pack(self):
        """Check sending of delivery notification on pack.

        The delivery notification is sent to the carrier when the pack is
        validated (the carrier has been configured this way), so the delivery
        notification should not be sent again when the ship is validated.
        """
        self.shipping.carrier_id = self.carrier_on_pack
        self._validate_picking(self.picking)
        self.assertEqual(self.picking.state, "done")
        # Validate the pack: delivery notification is sent with the
        # carrier of the ship, and this one is flagged accordingly
        with mock.patch.object(type(self.packing), "send_to_shipper") as mocked:
            self._validate_picking(self.packing)
            self.assertEqual(self.packing.state, "done")
            # stock.picking.send_to_shipper() not called at all
            mocked.assert_called()
            self.assertTrue(self.shipping.delivery_notification_sent)
        # Validate the ship: no delivery notification is sent to the carrier
        # as it has already been done during the validation of the pack
        with mock.patch.object(
            type(self.shipping.carrier_id), "send_shipping"
        ) as mocked:
            self._validate_picking(self.shipping)
            self.assertEqual(self.shipping.state, "done")
            # 'stock.picking.send_to_shipper()' has been called but nothing
            # happened because the ship is flagged, for that we are checking
            # if the 'delivery.carrier.send_shipping()' has not been called by
            # 'send_to_shipper'
            mocked.assert_not_called()
            self.assertTrue(self.shipping.delivery_notification_sent)
