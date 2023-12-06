# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockSplitPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        def _create_picking():
            return cls.env["stock.picking"].create(
                {
                    "partner_id": cls.partner.id,
                    "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                    "location_id": cls.src_location.id,
                    "location_dest_id": cls.dest_location.id,
                }
            )

        def _create_stock_move(product, picking):
            return cls.env["stock.move"].create(
                {
                    "name": "/",
                    "picking_id": picking.id,
                    "product_id": product.id,
                    "product_uom_qty": 10,
                    "product_uom": product.uom_id.id,
                    "location_id": cls.src_location.id,
                    "location_dest_id": cls.dest_location.id,
                }
            )

        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "detailed_type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "detailed_type": "product"}
        )
        cls.product_consu = cls.env["product.product"].create(
            {"name": "Test product", "detailed_type": "consu"}
        )
        cls.product_consu_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "detailed_type": "consu"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.picking = _create_picking()
        cls.move = _create_stock_move(cls.product, cls.picking)
        cls.move_2 = _create_stock_move(cls.product_2, cls.picking)
        cls.picking_consu = _create_picking()
        cls.move_consu = _create_stock_move(cls.product_consu, cls.picking_consu)
        cls.move_consu_2 = _create_stock_move(cls.product_consu_2, cls.picking_consu)

    def test_check_state_stock_split_picking(self):
        # Picking state is draft
        self.assertEqual(self.picking.state, "draft")
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Mark as todo this picking"):
            self.picking.split_process()

    def test_check_quantity_stock_split_picking(self):
        # Confirm picking
        self.picking.action_confirm()
        # We can't split a draft picking
        with self.assertRaisesRegex(
            UserError,
            "ou must enter quantity in order to split your picking in several ones",
        ):
            self.picking.split_process()

    def test_stock_split_picking_consumable(self):
        # Confirm picking
        self.picking_consu.action_confirm()
        move_line = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking_consu.id),
                ("product_id", "=", self.product_consu.id),
            ],
            limit=1,
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking_consu.id),
                ("product_id", "=", self.product_consu_2.id),
            ],
            limit=1,
        )
        self.move_consu.quantity = 4.0
        self.move_consu_2.quantity = 0.0
        # Split picking: 4 and 6
        self.picking_consu.split_process()

        # We have a picking with 4 units in state assigned
        self.assertAlmostEqual(move_line.quantity, 4.0)
        self.assertAlmostEqual(move_line.quantity_product_uom, 4.0)

        self.assertAlmostEqual(self.move_consu.quantity, 4.0)
        self.assertAlmostEqual(self.move_consu.product_qty, 4.0)
        self.assertAlmostEqual(self.move_consu.product_uom_qty, 4.0)

        self.assertEqual(move_line.picking_id, self.picking_consu)
        self.assertEqual(self.move_consu.picking_id, self.picking_consu)

        # move/move_line with no qty should no longer exist
        self.assertFalse(move_line_2.exists())
        self.assertFalse(self.move_consu_2.exists())

        self.assertEqual(self.picking_consu.state, "assigned")
        # Another one with 6 units in state assigned
        new_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking_consu.id)], limit=1
        )
        move_line = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_consu.id),
            ],
            limit=1,
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_consu_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move_line.quantity, 6.0)
        self.assertAlmostEqual(move_line.quantity_product_uom, 6.0)
        self.assertAlmostEqual(move_line_2.quantity, 10.0)
        self.assertAlmostEqual(move_line_2.quantity_product_uom, 10.0)

        move = self.env["stock.move"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_consu.id),
            ],
            limit=1,
        )
        move_2 = self.env["stock.move"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_consu_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move.quantity, 6.0)
        self.assertAlmostEqual(move.product_qty, 6.0)
        self.assertAlmostEqual(move.product_uom_qty, 6.0)
        self.assertAlmostEqual(move_2.quantity, 10.0)
        self.assertAlmostEqual(move_2.product_qty, 10.0)
        self.assertAlmostEqual(move_2.product_uom_qty, 10.0)

        self.assertEqual(new_picking.state, "assigned")

    def test_stock_split_picking_product_wo_stock(self):
        # Picking state is draft
        self.assertEqual(self.picking.state, "draft")
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Mark as todo this picking"):
            self.picking.split_process()
        # Confirm picking
        self.picking.action_confirm()
        self.assertFalse(
            self.env["stock.move.line"].search(
                [
                    ("picking_id", "=", self.picking.id),
                    ("product_id", "=", self.product.id),
                ],
                limit=1,
            )
        )
        self.assertFalse(
            self.env["stock.move.line"].search(
                [
                    ("picking_id", "=", self.picking.id),
                    ("product_id", "=", self.product_2.id),
                ],
                limit=1,
            )
        )
        self.move.quantity = 4.0
        self.move_2.quantity = 0.0
        # Split picking: 4 and 6
        self.picking.split_process()

        # We have a picking with 4 units in state assigned
        self.assertAlmostEqual(self.move.quantity, 4.0)
        self.assertAlmostEqual(self.move.product_qty, 4.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 4.0)

        self.assertEqual(self.move.picking_id, self.picking)

        # move/move_line with no qty should no longer exist
        self.assertFalse(self.move_2.exists())

        self.assertEqual(self.picking.state, "assigned")
        # Another one with 6 units in state assigned
        new_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking.id)], limit=1
        )
        self.assertFalse(
            self.env["stock.move.line"].search(
                [
                    ("picking_id", "=", new_picking.id),
                    ("product_id", "=", self.product.id),
                ],
                limit=1,
            )
        )
        self.assertFalse(
            self.env["stock.move.line"].search(
                [
                    ("picking_id", "=", new_picking.id),
                    ("product_id", "=", self.product_2.id),
                ],
                limit=1,
            )
        )

        move = self.env["stock.move"].search(
            [("picking_id", "=", new_picking.id), ("product_id", "=", self.product.id)],
            limit=1,
        )
        move_2 = self.env["stock.move"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move.quantity, 0.0)
        self.assertAlmostEqual(move.product_qty, 6.0)
        self.assertAlmostEqual(move.product_uom_qty, 6.0)
        self.assertAlmostEqual(move_2.quantity, 0.0)
        self.assertAlmostEqual(move_2.product_qty, 10.0)
        self.assertAlmostEqual(move_2.product_uom_qty, 10.0)

        self.assertEqual(new_picking.state, "confirmed")

    def test_stock_split_picking_product_with_stock(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.src_location.id,
                "quantity": 4,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.src_location.id,
                "quantity": 4,
            }
        )
        # Picking state is draft
        self.assertEqual(self.picking.state, "draft")
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Mark as todo this picking"):
            self.picking.split_process()
        # Confirm picking
        self.picking.action_confirm()
        move_line = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )
        self.move.quantity = 4.0
        self.move_2.quantity = 0.0
        # Split picking: 4 and 6
        self.picking.split_process()

        # We have a picking with 4 units in state assigned
        self.assertAlmostEqual(move_line.quantity, 4.0)
        self.assertAlmostEqual(move_line.quantity_product_uom, 4.0)

        self.assertAlmostEqual(self.move.quantity, 4.0)
        self.assertAlmostEqual(self.move.product_qty, 4.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 4.0)

        self.assertEqual(move_line.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)

        # move/move_line with no qty should no longer exist
        self.assertFalse(move_line_2.exists())
        self.assertFalse(self.move_2.exists())

        self.assertEqual(self.picking.state, "assigned")
        # Another one with 6 units in state assigned
        new_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking.id)], limit=1
        )
        self.assertFalse(
            self.env["stock.move.line"].search(
                [
                    ("picking_id", "=", new_picking.id),
                    ("product_id", "=", self.product.id),
                ],
                limit=1,
            )
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )
        self.assertAlmostEqual(move_line_2.quantity, 4.0)
        self.assertAlmostEqual(move_line_2.quantity_product_uom, 4.0)

        move = self.env["stock.move"].search(
            [("picking_id", "=", new_picking.id), ("product_id", "=", self.product.id)],
            limit=1,
        )
        move_2 = self.env["stock.move"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move.quantity, 0.0)
        self.assertAlmostEqual(move.product_qty, 6.0)
        self.assertAlmostEqual(move.product_uom_qty, 6.0)
        self.assertAlmostEqual(move_2.quantity, 4.0)
        self.assertAlmostEqual(move_2.product_qty, 10.0)
        self.assertAlmostEqual(move_2.product_uom_qty, 10.0)

        self.assertEqual(new_picking.state, "assigned")

    def test_stock_split_picking_wizard_move_consumable(self):
        self.move2 = self.move_consu.copy()
        self.assertEqual(self.move2.picking_id, self.picking_consu)
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking_consu.ids)
            .create({"mode": "move"})
        )
        wizard.action_apply()
        self.assertNotEqual(self.move2.picking_id, self.picking_consu)
        self.assertEqual(self.move_consu.picking_id, self.picking_consu)

    def test_stock_split_picking_wizard_move_product(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create({"mode": "move"})
        )
        wizard.action_apply()
        self.assertNotEqual(self.move2.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)

    def test_stock_split_picking_wizard_selection(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create({"mode": "selection", "move_ids": [(6, False, self.move2.ids)]})
        )
        wizard.action_apply()
        self.assertNotEqual(self.move2.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)

    def test_stock_picking_split_off_moves(self):
        with self.assertRaises(UserError):
            # fails because we can't split off all lines
            self.picking._split_off_moves(self.picking.move_ids)
        with self.assertRaises(UserError):
            # fails because we can't split cancelled pickings
            self.picking.action_cancel()
            self.picking._split_off_moves(self.picking.move_ids)
