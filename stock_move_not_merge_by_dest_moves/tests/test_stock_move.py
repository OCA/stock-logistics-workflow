# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

# from odoo.tests.common import HttpCase, TransactionCase
from odoo.addons.stock.tests.common import TestStockCommon


class TestStockMoveNotMergeByDestMoves(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tv = cls.env["product.product"].create(
            {
                "name": "Product Variable QTYs",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        # Enable pick_ship route
        cls.wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.id)], limit=1
        )
        # Get pick ship route and rules
        cls.wh.write({"delivery_steps": "pick_ship"})
        # Fixed procurement group
        cls.pick_ship_route = cls.wh.route_ids.filtered(
            lambda r: "(pick + ship)" in r.name
        )
        cls.pick_rule = cls.pick_ship_route.rule_ids.filtered(
            lambda rule: "Stock → Output" in rule.name
        )
        procurement_group = cls.env["procurement.group"].create({})
        cls.pick_rule.write(
            {
                "group_propagation_option": "fixed",
                "group_id": procurement_group.id,
            }
        )
        cls.ship_rule = cls.pick_ship_route.rule_ids - cls.pick_rule
        # Disable Backorder creation
        cls.wh.pick_type_id.write(
            {"create_backorder": "never", "reservation_method": "manual"}
        )
        cls.wh.out_type_id.write(
            {"create_backorder": "never", "reservation_method": "manual"}
        )

    def _create_pick_ship_pickings(self, same_destination_moves: bool = False):
        """Create pick and ship pickings with the given stock and move
        quantities linking pick and ship moves.

        :param same_destination_moves: If True, the destination moves will be the same
        """
        # Locations
        stock_location = self.pick_rule.location_src_id
        ship_location = self.pick_rule.location_dest_id
        customer_location = self.ship_rule.location_dest_id
        # Ensure stock
        self.env["stock.quant"]._update_available_quantity(
            self.product_tv, stock_location, 10.0
        )
        # PICK
        pick_picking = self.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "state": "draft",
            }
        )
        pick_move_1 = self.env["stock.move"].create(
            {
                "name": "pick move 1",
                "picking_id": pick_picking.id,
                "rule_id": self.pick_rule.id,
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "product_id": self.product_tv.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 7.0,
                "warehouse_id": self.wh.id,
                "group_id": self.pick_rule.group_id.id,
                "origin": "test_stock_move_not_merge_by_dest_moves",
                "procure_method": "make_to_stock",
            }
        )
        pick_move_2 = self.env["stock.move"].create(
            {
                "name": "pick move 2",
                "picking_id": pick_picking.id,
                "rule_id": self.pick_rule.id,
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "product_id": self.product_tv.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 3.0,
                "warehouse_id": self.wh.id,
                "group_id": self.pick_rule.group_id.id,
                "origin": "test_stock_move_not_merge_by_dest_moves",
                "procure_method": "make_to_stock",
            }
        )
        # SHIP
        ship_picking = self.env["stock.picking"].create(
            {
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": self.wh.out_type_id.id,
                "state": "confirmed",  # We don't want to confirm to avoid merge moves
            }
        )
        ship_move_1 = self.env["stock.move"].create(
            {
                "name": "ship move 1",
                "picking_id": ship_picking.id,
                "rule_id": self.ship_rule.id,
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "product_id": self.product_tv.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "warehouse_id": self.wh.id,
                "group_id": self.pick_rule.group_id.id,
                "origin": "test_stock_move_not_merge_by_dest_moves",
                "procure_method": "make_to_stock",
            }
        )
        # Link moves
        if same_destination_moves:
            (pick_move_1 | pick_move_2).write({"move_dest_ids": [(4, ship_move_1.id)]})
            ship_move_1.write(
                {"move_orig_ids": [(4, pick_move_1.id), (4, pick_move_2.id)]}
            )
        else:
            ship_move_1.write({"product_uom_qty": 7.0})
            ship_move_2 = self.env["stock.move"].create(
                {
                    "name": "ship move 2",
                    "picking_id": ship_picking.id,
                    "rule_id": self.ship_rule.id,
                    "location_id": ship_location.id,
                    "location_dest_id": customer_location.id,
                    "product_id": self.product_tv.id,
                    "product_uom": self.uom_unit.id,
                    "product_uom_qty": 3.0,
                    "warehouse_id": self.wh.id,
                    "group_id": self.pick_rule.group_id.id,
                    "origin": "test_stock_move_not_merge_by_dest_moves",
                    "procure_method": "make_to_stock",
                }
            )
            pick_move_1.write({"move_dest_ids": [(4, ship_move_1.id)]})
            pick_move_2.write({"move_dest_ids": [(4, ship_move_2.id)]})
            ship_move_1.write({"move_orig_ids": [(4, pick_move_1.id)]})
            ship_move_2.write({"move_orig_ids": [(4, pick_move_2.id)]})
        return pick_picking, ship_picking

    def test_merge_moves(self):
        """Test PICK merge moves when destination move is the same"""
        pick_picking, ship_picking = self._create_pick_ship_pickings(
            same_destination_moves=True,
        )
        self.assertEqual(len(pick_picking.move_ids), 2)
        pick_picking.action_confirm()
        self.assertEqual(len(pick_picking.move_ids), 1)

    def test_not_merge_moves(self):
        """Test PICK don't merge moves when destination moves are different"""
        pick_picking, ship_picking = self._create_pick_ship_pickings(
            same_destination_moves=False,
        )
        self.assertEqual(len(pick_picking.move_ids), 2)
        pick_picking.action_confirm()
        self.assertEqual(len(pick_picking.move_ids), 2)
