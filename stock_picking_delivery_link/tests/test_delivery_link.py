# Copyright 2021-2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import StockPickingDeliveryLinkCommonCase


class TestStockPickingDeliveryLink(StockPickingDeliveryLinkCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )

    def test_ship_data_from_pick(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pick_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move3 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2 | move3)._assign_picking()
        carrier = self.env.ref("delivery.free_delivery_carrier")
        move3.picking_id.carrier_id = carrier
        move1.move_dest_ids = move2
        move2.move_dest_ids = move3
        ship = move1.picking_id.ship_picking_id
        self.assertEqual(ship, move3.picking_id)
        self.assertEqual(ship.carrier_id, carrier)

    def test_ship_data_from_pack(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.out_type_id.id,
        )
        (move1 | move2)._assign_picking()
        carrier = self.env.ref("delivery.free_delivery_carrier")
        move2.picking_id.carrier_id = carrier
        move1.move_dest_ids = move2
        ship = move1.picking_id.ship_picking_id
        self.assertEqual(ship, move2.picking_id)
        self.assertEqual(ship.carrier_id, carrier)

    def test_ship_data_no_ship_found(self):
        move1 = self._create_move(
            self.product,
            self.stock_loc,
            self.shelf1_loc,
            picking_type_id=self.wh.pick_type_id.id,
        )
        move2 = self._create_move(
            self.product,
            self.shelf1_loc,
            self.shelf2_loc,
            picking_type_id=self.wh.pack_type_id.id,
        )
        (move1 | move2)._assign_picking()
        move1.move_dest_ids = move2
        self.assertFalse(move1.picking_id.ship_picking_id)
        self.assertFalse(move1.picking_id.ship_carrier_id)
