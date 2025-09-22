# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestCarrierPropagation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.warehouse.pick_type_id.reservation_method = "manual"
        cls.warehouse.out_type_id.reservation_method = "manual"
        # Disable carrier propagation on the pick rule
        # We want the one in the dynamic routing to play out
        cls.warehouse.delivery_route_id.rule_ids.filtered(
            lambda r: r.picking_type_id == cls.warehouse.pick_type_id
        ).propagate_carrier = False
        # Set up the products
        cls.product1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "consu", "is_storable": True}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "consu", "is_storable": True}
        )
        # Set up the locations
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.location_hb = cls.env["stock.location"].create(
            {"name": "Highbay", "location_id": cls.stock_location.id}
        )
        cls.location_handover = cls.env["stock.location"].create(
            {"name": "Handover", "location_id": cls.stock_location.id}
        )
        # Set up some stocks
        cls._update_product_qty_in_location(cls.location_hb, cls.product1, 100)
        cls._update_product_qty_in_location(cls.stock_location, cls.product2, 100)
        # Set up the dynamic routing
        cls.pick_type_routing = cls.env["stock.picking.type"].create(
            {
                "name": "Dynamic Routing",
                "code": "internal",
                "sequence_code": "WH/HO",
                "warehouse_id": cls.warehouse.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": cls.location_hb.id,
                "default_location_dest_id": cls.location_handover.id,
                "reservation_method": "manual",
            }
        )
        cls.routing = cls.env["stock.routing"].create(
            {
                "location_id": cls.location_hb.id,
                "picking_type_id": cls.warehouse.pick_type_id.id,
                "rule_ids": [
                    Command.create(
                        {
                            "method": "pull",
                            "picking_type_id": cls.pick_type_routing.id,
                            "propagate_carrier": True,
                        }
                    ),
                ],
            }
        )
        # Set up the test order
        cls.carrier_product = cls.env["product.product"].create(
            {
                "type": "service",
                "name": "Shipping costs",
                "standard_price": 10,
                "list_price": 100,
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "fixed_price": 50,
                "product_id": cls.carrier_product.id,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_4").id,
                "carrier_id": cls.carrier.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product1.id,
                            "product_uom_qty": 10,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product2.id,
                            "product_uom_qty": 10,
                        }
                    ),
                ],
            }
        )

    @classmethod
    def _update_product_qty_in_location(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def test_carrier_propagation(self):
        """Test that the carrier is propagated to the routing move"""
        self.order.action_confirm()
        # Check pick picking
        pick_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.pick_type_id
        )
        self.assertEqual(len(pick_picking), 1)
        pick_picking.action_assign()
        pick_picking.move_ids.picked = True
        pick_picking._action_done()
        # Check routing picking created and carrier propagated
        routing_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.pick_type_routing
        )
        self.assertEqual(len(routing_picking), 1)
        self.assertEqual(routing_picking.carrier_id, self.carrier)
        routing_picking.action_assign()
        routing_picking.move_ids.picked = True
        routing_picking._action_done()
        # Check ship picking created
        ship_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.out_type_id
        )
        self.assertEqual(len(ship_picking), 1)
        self.assertEqual(ship_picking.carrier_id, self.carrier)

    def test_no_carrier_propagation(self):
        """Test that the carrier is not propagated to the routing move"""
        self.routing.rule_ids.propagate_carrier = False
        self.order.action_confirm()
        # Check pick picking
        pick_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.pick_type_id
        )
        self.assertEqual(len(pick_picking), 1)
        pick_picking.action_assign()
        pick_picking.move_ids.picked = True
        pick_picking._action_done()
        # Check routing picking created and carrier propagated
        routing_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.pick_type_routing
        )
        self.assertEqual(len(routing_picking), 1)
        self.assertFalse(routing_picking.carrier_id)
        routing_picking.action_assign()
        routing_picking.move_ids.picked = True
        routing_picking._action_done()
        # Check ship picking created
        ship_picking = self.order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse.out_type_id
        )
        self.assertEqual(len(ship_picking), 1)
        self.assertEqual(ship_picking.carrier_id, self.carrier)
