# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPickingVariableQuantity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Variable Qty Product",
                "is_storable": True,
                "invoice_policy": "delivery",
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse Pick Ship",
                "code": "VPQ",
                "delivery_steps": "pick_ship",
            }
        )
        delivery_route = cls.warehouse.delivery_route_id
        # These tests target the regression on legacy pull-rule chains, so the
        # route is forced away from the newer push/pull setup.
        delivery_route.rule_ids[0].write(
            {"location_dest_id": delivery_route.rule_ids[1].location_src_id.id}
        )
        delivery_route.rule_ids[1].write({"action": "pull"})
        cls.pick_rule = delivery_route.rule_ids.filtered(
            lambda rule: rule.location_dest_id == cls.warehouse.wh_output_stock_loc_id
        )
        cls.ship_rule = delivery_route.rule_ids.filtered(
            lambda rule: rule.location_dest_id.usage == "customer"
        )
        cls.warehouse.pick_type_id.variable_quantity = True
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 40.0
        )

    def _create_pick_ship_pickings(self, stock_qty, move_qty):
        stock_location = self.pick_rule.location_src_id
        ship_location = self.pick_rule.location_dest_id
        customer_location = self.ship_rule.location_dest_id
        self.env["stock.quant"]._update_available_quantity(
            self.product, stock_location, stock_qty
        )
        pick_picking = self.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "picking_type_id": self.warehouse.pick_type_id.id,
            }
        )
        pick_move = self.env["stock.move"].create(
            {
                "name": "pick move",
                "picking_id": pick_picking.id,
                "rule_id": self.pick_rule.id,
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": move_qty,
                "warehouse_id": self.warehouse.id,
                "origin": "origin_max_qty",
                "procure_method": "make_to_stock",
            }
        )
        ship_picking = self.env["stock.picking"].create(
            {
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": self.warehouse.out_type_id.id,
            }
        )
        ship_move = self.env["stock.move"].create(
            {
                "name": "ship move",
                "picking_id": ship_picking.id,
                "rule_id": self.ship_rule.id,
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": move_qty,
                "warehouse_id": self.warehouse.id,
                "origin": "origin_max_qty",
                "procure_method": "make_to_stock",
            }
        )
        pick_move.write({"move_dest_ids": [(4, ship_move.id)]})
        ship_move.write({"move_orig_ids": [(4, pick_move.id)]})
        pick_picking.do_unreserve()
        ship_picking.do_unreserve()
        return pick_picking, ship_picking

    def _create_pick_ship_pickings_with_splits(
        self, stock_qty, pick_quantities, ship_quantities
    ):
        stock_location = self.pick_rule.location_src_id
        ship_location = self.pick_rule.location_dest_id
        customer_location = self.ship_rule.location_dest_id
        self.env["stock.quant"]._update_available_quantity(
            self.product, stock_location, stock_qty
        )
        pick_picking = self.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "picking_type_id": self.warehouse.pick_type_id.id,
            }
        )
        ship_picking = self.env["stock.picking"].create(
            {
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": self.warehouse.out_type_id.id,
            }
        )
        pick_moves = self.env["stock.move"]
        ship_moves = self.env["stock.move"]
        for index, quantity in enumerate(pick_quantities, start=1):
            pick_moves |= self.env["stock.move"].create(
                {
                    "name": f"pick move {index}",
                    "picking_id": pick_picking.id,
                    "rule_id": self.pick_rule.id,
                    "location_id": stock_location.id,
                    "location_dest_id": ship_location.id,
                    "product_id": self.product.id,
                    "product_uom": self.uom_unit.id,
                    "product_uom_qty": quantity,
                    "warehouse_id": self.warehouse.id,
                    "origin": "origin_split_qty",
                    "procure_method": "make_to_stock",
                }
            )
        for index, quantity in enumerate(ship_quantities, start=1):
            ship_moves |= self.env["stock.move"].create(
                {
                    "name": f"ship move {index}",
                    "picking_id": ship_picking.id,
                    "rule_id": self.ship_rule.id,
                    "location_id": ship_location.id,
                    "location_dest_id": customer_location.id,
                    "product_id": self.product.id,
                    "product_uom": self.uom_unit.id,
                    "product_uom_qty": quantity,
                    "warehouse_id": self.warehouse.id,
                    "origin": "origin_split_qty",
                    "procure_method": "make_to_stock",
                }
            )
        pick_moves.write({"move_dest_ids": [(6, 0, ship_moves.ids)]})
        ship_moves.write({"move_orig_ids": [(6, 0, pick_moves.ids)]})
        return pick_picking, ship_picking, pick_moves, ship_moves

    @classmethod
    def _create_sale_order(cls, quantity, product=None):
        product = product or cls.product
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                        }
                    )
                ],
            }
        )

    def _confirm_sale_and_get_pickings(self, ordered_qty, product=None):
        product = product or self.product
        order = self._create_sale_order(ordered_qty, product=product)
        order.action_confirm()
        self.assertEqual(len(order.picking_ids), 2)
        pick_picking = order.picking_ids.filtered(
            lambda picking: picking.location_dest_id
            == self.warehouse.wh_output_stock_loc_id
        )
        ship_picking = order.picking_ids.filtered(
            lambda picking: picking.location_dest_id.usage == "customer"
        )
        self.assertEqual(len(pick_picking), 1)
        self.assertEqual(len(ship_picking), 1)
        return order, pick_picking, ship_picking

    def _process_picking(self, picking, done_qty, cancel_backorder=False):
        picking.action_assign()
        move = picking.move_ids
        move.quantity = done_qty
        move.picked = True
        move._action_done(cancel_backorder=cancel_backorder)
        return move

    def _get_backorder(self, picking):
        return self.env["stock.picking"].search([("backorder_id", "=", picking.id)])

    def test_pick_ship_qty_done_exceeded(self):
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 1.0)
        pick_picking.action_assign()
        pick_picking.move_line_ids[0].quantity += 1.0
        pick_picking.button_validate()
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        self.assertEqual(ship_picking.move_line_ids[0].quantity, 2.0)
        ship_picking.button_validate()

    def test_pick_ship_qty_done_not_reached(self):
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 2.0)
        pick_picking.action_assign()
        pick_picking.button_validate()
        pick_picking.move_line_ids[0].quantity -= 1.0
        pick_picking.with_context(skip_sanity_check=True).button_validate()
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        self.assertEqual(ship_picking.move_line_ids[0].quantity, 1.0)
        ship_picking.with_context(skip_sanity_check=True).button_validate()

    def test_pick_ship_keeps_downstream_qty_when_disabled(self):
        self.warehouse.pick_type_id.variable_quantity = False
        pick_picking, ship_picking = self._create_pick_ship_pickings(2.0, 1.0)
        pick_picking.action_assign()
        pick_picking.move_line_ids[0].quantity += 1.0
        pick_picking.button_validate()
        ship_picking.do_unreserve()
        ship_picking.action_assign()
        self.assertEqual(ship_picking.move_line_ids[0].quantity, 1.0)

    def test_pick_ship_split_origins_spread_extra_across_dest_moves(self):
        _pick_picking, _ship_picking, pick_moves, ship_moves = (
            self._create_pick_ship_pickings_with_splits(20.0, [5.0, 5.0], [5.0, 5.0])
        )
        # Calling the helper directly isolates the redistribution logic from
        # move-line side effects so this regression stays focused on grouping.
        pick_moves.write({"quantity": 0.0})
        pick_moves[0].quantity = 6.0
        pick_moves[1].quantity = 5.0
        pick_moves._adjust_variable_quantity()
        self.assertEqual(ship_moves.sorted("id")[0].product_uom_qty, 6.0)
        self.assertEqual(ship_moves.sorted("id")[1].product_uom_qty, 5.0)

    def test_pick_ship_split_origins_zero_unneeded_dest_moves(self):
        _pick_picking, _ship_picking, pick_moves, ship_moves = (
            self._create_pick_ship_pickings_with_splits(20.0, [5.0, 5.0], [5.0, 5.0])
        )
        pick_moves.write({"quantity": 0.0})
        pick_moves[0].quantity = 2.0
        pick_moves[1].quantity = 3.0
        pick_moves._adjust_variable_quantity()
        self.assertEqual(ship_moves.sorted("id")[0].product_uom_qty, 5.0)
        self.assertEqual(ship_moves.sorted("id")[1].product_uom_qty, 0.0)

    def test_pick_extra_updates_ship_move_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        self.assertTrue(
            order.order_line.filtered(lambda line: line.product_id == self.product)
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_picking(pick_picking, 12.0)
        self.assertEqual(ship_move.product_uom_qty, 12.0)

    def test_pick_partial_cancel_backorder_updates_ship_move_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        self.assertTrue(
            order.order_line.filtered(lambda line: line.product_id == self.product)
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_picking(pick_picking, 6.0, cancel_backorder=True)
        self.assertFalse(self._get_backorder(pick_picking))
        self.assertEqual(ship_move.product_uom_qty, 6.0)

    def test_pick_partial_then_extra_backorder_updates_ship_move_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        self.assertTrue(
            order.order_line.filtered(lambda line: line.product_id == self.product)
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_picking(pick_picking, 6.0)
        backorder_pick = self._get_backorder(pick_picking)
        self.assertEqual(len(backorder_pick), 1)
        self.assertEqual(backorder_pick.move_ids.product_uom_qty, 4.0)
        self.assertEqual(ship_move.product_uom_qty, 6.0)
        self._process_picking(backorder_pick, 5.0, cancel_backorder=True)
        customer_moves = order.picking_ids.filtered(
            lambda picking: picking.location_dest_id.usage == "customer"
        ).move_ids.filtered(lambda move: move.product_id == self.product)
        self.assertEqual(sum(customer_moves.mapped("product_uom_qty")), 11.0)

    def test_pick_exact_quantity_keeps_ship_move_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        self.assertTrue(
            order.order_line.filtered(lambda line: line.product_id == self.product)
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_picking(pick_picking, 10.0)
        self.assertEqual(ship_move.product_uom_qty, 10.0)

    def test_pick_keeps_ship_move_qty_when_disabled(self):
        self.warehouse.pick_type_id.variable_quantity = False
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        self.assertTrue(
            order.order_line.filtered(lambda line: line.product_id == self.product)
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_picking(pick_picking, 12.0)
        self.assertEqual(ship_move.product_uom_qty, 10.0)
