# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.addons.stock.tests.common import TestStockCommon


class TestStockRuleReservation(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tv = cls.env["product.product"].create(
            {
                "name": "Product Variable QTYs",
                "type": "consu",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "is_storable": True,
                "tracking": "none",
            }
        )
        # Enable pick_ship route and set the pick rule to reserve_max_quantity
        cls.wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.id)], limit=1
        )
        # Get pick ship route and rules
        cls.wh.write({"delivery_steps": "pick_ship"})
        cls.pick_ship_route = cls.wh.route_ids.filtered(
            lambda r: "(pick + ship)" in r.name
        )
        procurement_group = cls.env["procurement.group"].create({})
        cls.pick_rule = cls.pick_ship_route.rule_ids[0]
        cls.pick_rule.write(
            {
                "location_dest_id": cls.wh.wh_output_stock_loc_id.id,
                "group_propagation_option": "fixed",
                "group_id": procurement_group.id,
            }
        )
        # Activate the reserve_max_quantity on the push rule and make it pull
        # We don't want to chain pickings, we want to be created all at once
        cls.ship_rule = cls.pick_ship_route.rule_ids[-1]
        cls.ship_rule.write(
            {
                "action": "pull",
                "location_src_id": cls.wh.wh_output_stock_loc_id.id,
                "reserve_max_quantity": True,
            }
        )
        # Disable Backorder creation
        cls.wh.pick_type_id.write({"create_backorder": "never"})
        cls.wh.out_type_id.write({"create_backorder": "never"})

    def _create_pick_ship_pickings(self, stock_qty: float, move_qty: float):
        """Create pick and ship pickings with the given stock and move quantities"""
        # Locations
        stock_location = self.pick_rule.location_src_id
        ship_location = self.pick_rule.location_dest_id
        customer_location = self.ship_rule.location_dest_id
        # Ensure stock
        self.env["stock.quant"]._update_available_quantity(
            self.product_tv, stock_location, stock_qty
        )
        # PICK
        pick_picking = self.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "picking_type_id": self.wh.pick_type_id.id,
            }
        )
        pick_move = self.env["stock.move"].create(
            {
                "name": "pick move",
                "picking_id": pick_picking.id,
                "rule_id": self.pick_rule.id,
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "product_id": self.product_tv.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": move_qty,
                "warehouse_id": self.wh.id,
                "group_id": self.pick_rule.group_id.id,
                "origin": "origin_max_qty",
                "procure_method": "make_to_stock",
            }
        )
        # SHIP
        ship_picking = self.env["stock.picking"].create(
            {
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": self.wh.out_type_id.id,
            }
        )
        ship_move = self.env["stock.move"].create(
            {
                "name": "ship move",
                "picking_id": ship_picking.id,
                "rule_id": self.ship_rule.id,
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "product_id": self.product_tv.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": move_qty,
                "warehouse_id": self.wh.id,
                "group_id": self.pick_rule.group_id.id,
                "origin": "origin_max_qty",
                "procure_method": "make_to_stock",
            }
        )
        # Link moves
        pick_move.write({"move_dest_ids": [(4, ship_move.id)]})
        ship_move.write({"move_orig_ids": [(4, pick_move.id)]})
        # Unreserve
        pick_picking.do_unreserve()
        ship_picking.do_unreserve()
        return pick_picking, ship_picking

    def test_pick_ship_qty_done_exceeded(self):
        """Test picking flow when qty done exceedes the demand in pick"""
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 1.0)
        # Operations on PICK from scratch
        pick_picking.action_assign()
        pick_picking.move_line_ids[0].quantity += 1.0
        pick_picking.button_validate()
        # Operations on SHIP from scratch
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        self.assertEqual(ship_picking.move_line_ids[0].quantity, 2.0)
        ship_picking.button_validate()

    def test_pick_ship_qty_done_not_reached(self):
        """Test picking flow when qty done not reachs the demand in pick"""
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 2.0)
        # Operations on PICK from scratch
        pick_picking.action_assign()
        pick_picking.move_line_ids[0].quantity -= 1.0
        pick_picking.with_context(skip_sanity_check=True).button_validate()
        # Operations on SHIP from scratch
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        self.assertEqual(ship_picking.move_line_ids[0].quantity, 1.0)
        ship_picking.with_context(skip_sanity_check=True).button_validate()
