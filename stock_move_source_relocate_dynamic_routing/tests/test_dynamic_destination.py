from odoo.addons.stock_dynamic_routing.tests.test_routing_pull import (
    TestRoutingPullCommon,
)


class TestRoutingAndSourceRelocate(TestRoutingPullCommon):
    def test_pickship_with_routing_and_relocate(self):
        """Check that if a pick move is partially available, the ship move is not split

        When a pick move is partially available and the destination is
        re-routed, it is split in 2 moves, one assigned on the re-routed
        destination location and one not assigned relocated and then re-routed
        to that same destination location. As both pick moves are going to the
        same destination location, ensure the ship move is not split.

        This test is similar to test_change_dest_move_source_split in
        stock_dynamic_routing/tests/test_routing_pull except that no move_d is created"""

        self.env["stock.source.relocate"].create(
            {
                "location_id": self.wh.lot_stock_id.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "relocate_location_id": self.location_hb.id,
                "rule_domain": "[]",
            }
        )

        area1 = self.env["stock.location"].create(
            {"location_id": self.wh.wh_output_stock_loc_id.id, "name": "Area1"}
        )
        self.pick_type_routing_op.default_location_dest_id = area1

        pick_type_routing_delivery = self.env["stock.picking.type"].create(
            {
                "name": "Delivery (after routing)",
                "code": "outgoing",
                "sequence_code": "OUT(R)",
                "warehouse_id": self.wh.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": area1.id,
                "default_location_dest_id": self.customer_loc.id,
            }
        )
        self.env["stock.routing"].create(
            {
                "location_id": area1.id,
                "picking_type_id": self.wh.out_type_id.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "method": "pull",
                            "picking_type_id": pick_type_routing_delivery.id,
                        },
                    )
                ],
            }
        )

        pick_picking, customer_picking = self._create_pick_ship(
            self.wh, [(self.product1, 10)]
        )
        move_a = pick_picking.move_lines
        move_b = customer_picking.move_lines

        self._update_product_qty_in_location(self.location_hb_1_2, move_a.product_id, 6)
        pick_picking.action_assign()

        move_c = (
            self.env["stock.picking"]
            .search([("picking_type_id", "=", self.pick_type_routing_op.id)])
            .move_lines
        )[0]
        self.assertRecordValues(
            move_a | move_b | move_c,
            [
                {
                    "product_qty": 4,
                    "move_orig_ids": [],
                    "move_dest_ids": move_b.ids,
                    "state": "confirmed",
                    "location_id": self.location_hb.id,
                    "location_dest_id": area1.id,
                },
                {
                    "product_qty": 10,
                    "move_orig_ids": (move_c | move_a).ids,
                    "move_dest_ids": [],
                    "state": "waiting",
                    "location_id": area1.id,
                    "location_dest_id": self.customer_loc.id,
                },
                {
                    "product_qty": 6,
                    "move_orig_ids": [],
                    "move_dest_ids": move_b.ids,
                    "state": "assigned",
                    "location_id": self.location_hb.id,
                    "location_dest_id": area1.id,
                },
            ],
        )

        self.assertEqual(move_a.picking_id.picking_type_id, self.pick_type_routing_op)
        self.assertEqual(move_b.picking_id.picking_type_id, pick_type_routing_delivery)
        self.assertEqual(move_c.picking_id.picking_type_id, self.pick_type_routing_op)

    def test_prepickship_with_routing_and_relocate(self):
        """Check that if a pick move is waiting another move, the ship move is not split

        When a pick move is partially available with a new additional pre-pick
        step and the destination is re-routed, it is split in 2 moves, one
        waiting the new move on the re-routed destination location and one not
        assigned relocated and then re-routed to that same destination
        location. As both pick moves are going to the same destination
        location, ensure the ship move is not split.

        This test is similar to test_change_dest_move_source_split and
        test_change_dest_move_source_chain in
        stock_dynamic_routing/tests/test_routing_pull except that no move_d is
        created"""

        self.env["stock.source.relocate"].create(
            {
                "location_id": self.wh.lot_stock_id.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "relocate_location_id": self.location_hb.id,
                "rule_domain": "[]",
            }
        )

        # Configure Pre-Pick routing
        location_shu = self.env["stock.location"].create(
            {"location_id": self.location_hb.id, "name": "SHU"}
        )
        prepick_pick_type = self.env["stock.picking.type"].create(
            {
                "name": "PrePick",
                "code": "internal",
                "sequence_code": "WH/SHU",
                "warehouse_id": self.wh.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": location_shu.id,
                "default_location_dest_id": self.location_hb.id,
            }
        )
        self.env["stock.routing"].create(
            {
                "location_id": location_shu.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "rule_ids": [
                    (0, 0, {"method": "pull", "picking_type_id": prepick_pick_type.id})
                ],
            }
        )

        # Configure Pick-Ship routing
        area1 = self.env["stock.location"].create(
            {"location_id": self.wh.wh_output_stock_loc_id.id, "name": "Area1"}
        )
        self.pick_type_routing_op.default_location_dest_id = area1

        pick_type_routing_delivery = self.env["stock.picking.type"].create(
            {
                "name": "Delivery (after routing)",
                "code": "outgoing",
                "sequence_code": "OUT(R)",
                "warehouse_id": self.wh.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": area1.id,
                "default_location_dest_id": self.customer_loc.id,
            }
        )
        self.env["stock.routing"].create(
            {
                "location_id": area1.id,
                "picking_type_id": self.wh.out_type_id.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "method": "pull",
                            "picking_type_id": pick_type_routing_delivery.id,
                        },
                    )
                ],
            }
        )

        pick_picking, customer_picking = self._create_pick_ship(
            self.wh, [(self.product1, 10)]
        )
        move_a = pick_picking.move_lines
        move_b = customer_picking.move_lines

        self._update_product_qty_in_location(location_shu, move_a.product_id, 6)
        pick_picking.action_assign()

        move_d = (
            self.env["stock.picking"]
            .search([("picking_type_id", "=", prepick_pick_type.id)])
            .move_lines
        )
        move_c = (
            self.env["stock.picking"]
            .search([("picking_type_id", "=", self.pick_type_routing_op.id)])
            .move_lines
        )[0]
        self.assertRecordValues(
            move_a | move_b | move_c | move_d,
            [
                {
                    "product_qty": 4,
                    "move_orig_ids": [],
                    "move_dest_ids": move_b.ids,
                    "state": "confirmed",
                    "location_id": self.location_hb.id,
                    "location_dest_id": area1.id,
                },
                {
                    "product_qty": 10,
                    "move_orig_ids": (move_c | move_a).ids,
                    "move_dest_ids": [],
                    "state": "waiting",
                    "location_id": area1.id,
                    "location_dest_id": self.customer_loc.id,
                },
                {
                    "product_qty": 6,
                    "move_orig_ids": move_d.ids,
                    "move_dest_ids": move_b.ids,
                    "state": "waiting",
                    "location_id": self.location_hb.id,
                    "location_dest_id": area1.id,
                },
                {
                    "product_qty": 6,
                    "move_orig_ids": [],
                    "move_dest_ids": move_c.ids,
                    "state": "assigned",
                    "location_id": location_shu.id,
                    "location_dest_id": self.location_hb.id,
                },
            ],
        )

        self.assertEqual(move_a.picking_id.picking_type_id, self.pick_type_routing_op)
        self.assertEqual(move_b.picking_id.picking_type_id, pick_type_routing_delivery)
        self.assertEqual(move_c.picking_id.picking_type_id, self.pick_type_routing_op)
