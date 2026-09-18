# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingVariableQtyPackaging(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Variable Packaging Product", "is_storable": True}
        )
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "3 kg package", "product_id": cls.product.id, "qty": 3}
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Variable Packaging Warehouse",
                "code": "VPQ",
                "delivery_steps": "pick_ship",
            }
        )
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pick_type.propagate_variable_qty = True
        delivery_route = cls.warehouse.delivery_route_id
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

    def _create_pick_ship_moves(self, product, quantity, packaging):
        stock_location = self.pick_rule.location_src_id
        ship_location = self.pick_rule.location_dest_id
        customer_location = self.ship_rule.location_dest_id
        pick_picking = self.env["stock.picking"].create(
            {
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "picking_type_id": self.pick_type.id,
            }
        )
        ship_picking = self.env["stock.picking"].create(
            {
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": self.warehouse.out_type_id.id,
            }
        )
        pick_move = self.env["stock.move"].create(
            {
                "name": "pick move",
                "picking_id": pick_picking.id,
                "rule_id": self.pick_rule.id,
                "location_id": stock_location.id,
                "location_dest_id": ship_location.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": quantity,
                "product_packaging_id": packaging.id,
                "warehouse_id": self.warehouse.id,
                "procure_method": "make_to_stock",
            }
        )
        ship_move = self.env["stock.move"].create(
            {
                "name": "ship move",
                "picking_id": ship_picking.id,
                "rule_id": self.ship_rule.id,
                "location_id": ship_location.id,
                "location_dest_id": customer_location.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": quantity,
                "product_packaging_id": packaging.id,
                "warehouse_id": self.warehouse.id,
                "procure_method": "make_to_stock",
            }
        )
        pick_move.write({"move_dest_ids": [Command.link(ship_move.id)]})
        ship_move.write({"move_orig_ids": [Command.link(pick_move.id)]})
        return pick_picking, ship_picking, pick_move, ship_move

    def test_variable_quantity_keeps_done_packaging_on_delivery(self):
        stock_location = self.pick_rule.location_src_id
        self.env["stock.quant"]._update_available_quantity(
            self.product, stock_location, 10
        )
        pick_picking, ship_picking, pick_move, ship_move = self._create_pick_ship_moves(
            self.product, 6, self.packaging
        )

        pick_picking.action_assign()
        pick_move.quantity = 3.3
        pick_move.move_line_ids.product_packaging_quantity = 2
        pick_move.picked = True
        pick_move._action_done(cancel_backorder=True)

        ship_picking.action_assign()
        self.assertEqual(ship_move.product_uom_qty, 3.3)
        self.assertEqual(ship_move.move_line_ids.product_packaging_qty, 2)

    def test_variable_quantity_keeps_done_packaging_by_lot(self):
        product = self.env["product.product"].create(
            {
                "name": "Lot Variable Packaging Product",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        packaging = self.env["product.packaging"].create(
            {"name": "Single package", "product_id": product.id, "qty": 1}
        )
        lots = self.env["stock.lot"].create(
            [
                {"name": "Lot A", "product_id": product.id},
                {"name": "Lot B", "product_id": product.id},
                {"name": "Lot C", "product_id": product.id},
            ]
        )
        source_packaging_by_lot = dict(zip(lots.ids, (2, 4, 5), strict=True))
        stock_location = self.pick_rule.location_src_id
        for lot, quantity in zip(lots, (3, 2, 5), strict=True):
            self.env["stock.quant"]._update_available_quantity(
                product, stock_location, quantity, lot_id=lot
            )
        pick_picking, ship_picking, pick_move, ship_move = self._create_pick_ship_moves(
            product, 10, packaging
        )

        pick_picking.action_assign()
        for line in pick_move.move_line_ids:
            line.product_packaging_quantity = source_packaging_by_lot[line.lot_id.id]
        pick_move.picked = True
        pick_move._action_done(cancel_backorder=True)

        ship_picking.action_assign()
        self.assertEqual(len(ship_move.move_line_ids), 3)
        for line in ship_move.move_line_ids:
            self.assertEqual(
                line.product_packaging_qty,
                source_packaging_by_lot[line.lot_id.id],
            )
