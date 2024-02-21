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
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
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
        # Activate the reserve_max_quantity on the push rule
        cls.ship_rule.write({"reserve_max_quantity": True})
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
        pick_picking.action_set_quantities_to_reservation()
        pick_picking.move_line_ids[0].qty_done += 1.0
        pick_picking.button_validate()
        # Operations on SHIP from scratch
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        ship_picking.action_set_quantities_to_reservation()
        self.assertEqual(ship_picking.move_line_ids[0].qty_done, 2.0)
        ship_picking.button_validate()

    def test_pick_ship_qty_done_not_reached(self):
        """Test picking flow when qty done not reachs the demand in pick"""
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 2.0)
        # Operations on PICK from scratch
        pick_picking.action_assign()
        pick_picking.action_set_quantities_to_reservation()
        pick_picking.move_line_ids[0].qty_done -= 1.0
        pick_picking.with_context(skip_sanity_check=True).button_validate()
        # Operations on SHIP from scratch
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        ship_picking.action_set_quantities_to_reservation()
        self.assertEqual(ship_picking.move_line_ids[0].qty_done, 1.0)
        ship_picking.with_context(skip_sanity_check=True).button_validate()
