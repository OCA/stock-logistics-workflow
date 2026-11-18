# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestPushRuleDestination(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.reception_steps = "two_steps"
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product test",
                "is_storable": True,
            }
        )

        # Create a sub location of input to receive products
        cls.input_1 = cls.env["stock.location"].create(
            {
                "name": "Input 1",
                "location_id": cls.warehouse.wh_input_stock_loc_id.id,
            }
        )

        cls.route = cls.env["stock.route"].create(
            {
                "name": "Receive and Push",
            }
        )

        # Create a Push Rule to create automatically a move to Stock
        # and trigger putaways
        cls.pick_type = cls.env["stock.picking.type"].create(
            {
                "name": "Put away Input -> Stock",
                "default_location_src_id": cls.warehouse.wh_input_stock_loc_id.id,
                "default_location_dest_id": cls.warehouse.lot_stock_id.id,
                "sequence_code": "PUTAW/",
            }
        )
        cls.rule = cls.env["stock.rule"].create(
            {
                "name": "Input -> Stock",
                "action": "push",
                "picking_type_id": cls.pick_type.id,
                "use_rule_destination_location": True,
                "location_dest_id": cls.warehouse.lot_stock_id.id,
                "location_src_id": cls.warehouse.wh_input_stock_loc_id.id,
                "route_id": cls.route.id,
                "warehouse_id": cls.warehouse.id,
            }
        )
        cls.warehouse.route_ids |= cls.route

        # Input should be taken in Stock, so put it as child
        cls.warehouse.wh_input_stock_loc_id.location_id = cls.warehouse.lot_stock_id

    def test_push_rule_destination(self):
        # Create a move from suppliers to Input
        move_in = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "location_final_id": self.warehouse.wh_input_stock_loc_id.id,
            }
        )

        move_before = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        move_in._action_confirm()
        move_in._action_assign()

        self.assertEqual(
            "assigned",
            move_in.state,
        )

        self.assertFalse(move_before)

        move_in.move_line_ids.location_dest_id = self.input_1
        move_in.move_line_ids.picked = True
        move_in._action_done()

        self.assertEqual("done", move_in.state)

        move_put_away = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        self.assertTrue(move_put_away)

    def test_push_rule_destination_no_move(self):
        self.rule.use_rule_destination_location = False
        # Create a move from suppliers to Input
        move_in = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "location_final_id": self.warehouse.wh_input_stock_loc_id.id,
            }
        )

        move_before = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        move_in._action_confirm()
        move_in._action_assign()

        self.assertEqual(
            "assigned",
            move_in.state,
        )

        self.assertFalse(move_before)

        move_in.move_line_ids.location_dest_id = self.input_1
        move_in.move_line_ids.picked = True
        move_in._action_done()

        self.assertEqual("done", move_in.state)

        move_put_away = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        self.assertFalse(move_put_away)
