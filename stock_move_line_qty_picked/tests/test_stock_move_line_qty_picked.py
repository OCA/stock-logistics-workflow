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
        cls.product = cls.env.ref("product.product_product_9")

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

    def test_move_pick_qty(self):
        move = self._create_move(
            self.product, 5.0, self.stock_location, self.stock_location_2
        )
        move_line = move.move_line_ids
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 0)
        self.assertFalse(move_line.picked)
        # Pick partial qty
        move_line.qty_picked = 3
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 3)
        self.assertTrue(move_line.picked)
        # Updating 'picked' to True should not reset the picked qty
        move_line.picked = True
        self.assertEqual(move_line.quantity, 5)
        self.assertEqual(move_line.qty_picked, 3)
        self.assertTrue(move_line.picked)
        # When validating, only the picked qty is moved
        move.picking_id.with_context(skip_backorder=True).button_validate()
        self.assertEqual(move_line.quantity, 3)

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
