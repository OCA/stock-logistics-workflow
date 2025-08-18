# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestStockMoveLineQtyPicked(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        group_stock_multi_locations = cls.env.ref("stock.group_stock_multi_locations")
        group_production_lot = cls.env.ref("stock.group_production_lot")
        cls.env.user.write(
            {
                "groups_id": [
                    (4, group_stock_multi_locations.id),
                    (4, group_production_lot.id),
                ]
            }
        )
        cls.internal_transfer_type = cls.env.ref("stock.picking_type_internal")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_2 = cls.stock_location.copy({"name": "stock 2"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 100
        )
        cls.quant = cls.env["stock.quant"]._gather(cls.product, cls.stock_location)

    @classmethod
    def _create_move(cls, product, quantity, from_location, to_location, picking=None):
        if picking is None:
            picking = cls._create_transfer(from_location, to_location)
        picking_form = Form(picking)
        picking_moves = picking.move_ids
        with picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = product
            move_form.product_uom_qty = quantity
        picking = picking_form.save()
        if picking.state == "draft":
            picking.action_confirm()
        return picking.move_ids - picking_moves

    @classmethod
    def _create_transfer(cls, from_location, to_location):
        picking_form = Form(
            cls.env["stock.picking"].with_context(
                default_picking_type_id=cls.internal_transfer_type.id
            )
        )
        picking_form.location_id = from_location
        picking_form.location_dest_id = to_location
        return picking_form.save()

    def test_move_pick_qty_reservation(self):
        move = self._create_move(
            self.product, 5.0, self.stock_location, self.stock_location_2
        )
        move_line = move.move_line_ids
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move.quantity, 5)
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 0)
        self.assertFalse(move_line.picked)
        self.assertEqual(self.quant.reserved_quantity, 5)
        # Pick partial qty
        move_line.qty_picked = 4
        self.assertEqual(move.quantity, 5)
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 4)
        self.assertTrue(move_line.picked)
        self.assertEqual(self.quant.reserved_quantity, 5)
        # Decrease picked qty on move line
        move_line.qty_picked = 3
        self.assertEqual(move.quantity, 5)
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 3)
        self.assertTrue(move_line.picked)
        self.assertEqual(self.quant.reserved_quantity, 5)
        # Decrease reserved qty on move
        move.quantity = 2
        self.assertEqual(move.quantity, 2)
        self.assertEqual(move_line.quantity, 2)
        self.assertEqual(self.quant.reserved_quantity, 2)
        self.assertEqual(move_line.qty_picked, 3)
        self.assertTrue(move_line.picked)
        # When validating, only the picked qty is moved, quantity is updated on
        #  stock.move and another move line is created to match qty_picked
        move.picking_id.with_context(skip_backorder=True).button_validate()
        self.assertEqual(move.quantity, 3)
        self.assertEqual(sum(move.move_line_ids.mapped("quantity")), 3)
        # Ensure 3 were moved on the quant and 2 are reserved on backorder
        self.assertEqual(self.quant.quantity, 97)
        self.assertEqual(self.quant.reserved_quantity, 2)

    def test_move_concurrent_pick_qty(self):
        move = self._create_move(
            self.product, 10.0, self.stock_location, self.stock_location_2
        )
        move_line = move.move_line_ids
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move_line.quantity, 10)
        self.assertEqual(move_line.qty_picked, 0)
        self.assertFalse(move_line.picked)
        move_line.qty_picked = 5
        self.assertEqual(move_line.quantity, 10)
        self.assertEqual(move_line.qty_picked, 5)
        self.assertTrue(move_line.picked)
        move_form = Form(move, view="stock.view_stock_move_operations")
        with move_form.move_line_ids.new():
            pass
        move_form.save()
        self.assertEqual(len(move.move_line_ids), 2)
        new_line = move.move_line_ids - move_line
        new_line.qty_picked = 3
        self.assertEqual(sum(ml.quantity for ml in move.move_line_ids), 10)
        move.picking_id.with_context(skip_backorder=True).button_validate()
        self.assertEqual(move.quantity, 8)

    def test_move_unpick_qty(self):
        move = self._create_move(
            self.product, 5.0, self.stock_location, self.stock_location_2
        )
        move_line = move.move_line_ids
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 0)
        self.assertFalse(move_line.picked)
        # Pick
        move_line.picked = True
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 5)
        self.assertTrue(move_line.picked)
        # Unpick
        move_line.picked = False
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 0)
        self.assertFalse(move_line.picked)

    def test_mls_picked_and_not_picked(self):
        product = self.env["product.product"].create(
            {"name": "Test product", "is_storable": True, "tracking": "lot"}
        )

        lot_map = {}
        for lot_name in ["LOT-001", "LOT-002", "LOT-003", "LOT-004"]:
            lot = self.env["stock.lot"].create(
                {
                    "name": lot_name,
                    "product_id": product.id,
                }
            )
            lot_map[lot_name] = lot
            self.env["stock.quant"]._update_available_quantity(
                product, self.stock_location, 10, lot_id=lot
            )
        move = self._create_move(
            product, 40.0, self.stock_location, self.stock_location_2
        )
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move.quantity, 40)
        self.assertFalse(move.picked)
        self.assertEqual(len(move.move_line_ids), 4)
        for line in move.move_line_ids:
            self.assertEqual(line.quantity, 10)
            self.assertEqual(line.qty_picked, 0)
            self.assertFalse(line.picked)
        # Setting picked on either move or move line will:
        #  - mark picked on both move and move lines through compute and inverse
        #  - set qty_picked = quantity
        move.picked = True

        # Remove picked flag on LOT-001
        lot_1_line = move.move_line_ids.filtered(lambda li: li.lot_id.name == "LOT-001")
        lot_1_line.picked = False
        # Change quantity picked on LOT-002
        lot_2_line = move.move_line_ids.filtered(lambda li: li.lot_id.name == "LOT-002")
        lot_2_line.qty_picked = 8
        # Keep qty_picked to 10 and picked=True on LOT-003
        lot_3_line = move.move_line_ids.filtered(lambda li: li.lot_id.name == "LOT-003")
        # Set qty_picked to 0 on LOT-004
        lot_4_line = move.move_line_ids.filtered(lambda li: li.lot_id.name == "LOT-004")
        lot_4_line.qty_picked = 0

        self.assertEqual(lot_1_line.quantity, 10)
        self.assertEqual(lot_1_line.qty_picked, 0)
        self.assertFalse(lot_1_line.picked)

        self.assertEqual(lot_2_line.quantity, 10)
        self.assertEqual(lot_2_line.qty_picked, 8)
        self.assertTrue(lot_2_line.picked)

        self.assertEqual(lot_3_line.quantity, 10)
        self.assertEqual(lot_3_line.qty_picked, 10)
        self.assertTrue(lot_3_line.picked)

        self.assertEqual(lot_4_line.quantity, 10)
        self.assertEqual(lot_4_line.qty_picked, 0)
        self.assertFalse(lot_4_line.picked)

        # When validating we must have
        #  - LOT-001: not moved because picked is False
        #  - LOT-002: 8pces moved according to qty_picked
        #  - LOT-003: 10pces moved because picked is True and qty_picked
        #  - LOT-004: not moved because qty_picked = 0
        move.picking_id.with_context(skip_backorder=True).button_validate()

        lot_1_quant = self.env["stock.quant"]._gather(
            product, self.stock_location, lot_id=lot_map["LOT-001"]
        )
        self.assertEqual(lot_1_quant.quantity, 10)

        lot_2_quant = self.env["stock.quant"]._gather(
            product, self.stock_location, lot_id=lot_map["LOT-002"]
        )
        self.assertEqual(lot_2_quant.quantity, 2)
        lot_2_quant_2 = self.env["stock.quant"]._gather(
            product, self.stock_location_2, lot_id=lot_map["LOT-002"]
        )
        self.assertEqual(lot_2_quant_2.quantity, 8)

        lot_3_quant = self.env["stock.quant"]._gather(
            product, self.stock_location, lot_id=lot_map["LOT-003"]
        )
        self.assertEqual(lot_3_quant.quantity, 0)
        lot_3_quant_2 = self.env["stock.quant"]._gather(
            product, self.stock_location_2, lot_id=lot_map["LOT-003"]
        )
        self.assertEqual(lot_3_quant_2.quantity, 10)

        lot_4_quant = self.env["stock.quant"]._gather(
            product, self.stock_location, lot_id=lot_map["LOT-004"]
        )
        self.assertEqual(lot_4_quant.quantity, 10)
