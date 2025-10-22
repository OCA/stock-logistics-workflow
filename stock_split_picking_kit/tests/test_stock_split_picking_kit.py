# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import RecordCapturer

from odoo.addons.stock_split_picking.tests.common import TestStockSplitPickingCase


class TestStockSplitPickingKit(TestStockSplitPickingCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_garden_table = cls.env["product.product"].create(
            {
                "name": "GARDEN TABLE",
                "type": "consu",
                "sale_ok": True,
                "purchase_ok": True,
            }
        )
        cls.product_garden_table_top = cls.env["product.product"].create(
            {
                "name": "GARDEN TABLE TOP",
                "type": "consu",
                "is_storable": True,
                "sale_ok": True,
            }
        )
        cls.product_garden_table_leg = cls.env["product.product"].create(
            {
                "name": "GARDEN TABLE LEG",
                "type": "consu",
                "is_storable": True,
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.bom_garden_table = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_garden_table.product_tmpl_id.id,
                "product_id": cls.product_garden_table.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_leg.id,
                            "product_qty": 4.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_top.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    @classmethod
    def _get_kit_quantity(cls, picking, bom):
        """Returns the quantity of kits in a transfer."""
        filters = {
            "incoming_moves": lambda m: True,
            "outgoing_moves": lambda m: False,
        }
        kit_quantity = picking.move_ids._compute_kit_quantities(
            bom.product_id, max(picking.move_ids.mapped("product_qty")), bom, filters
        )
        return kit_quantity

    @classmethod
    def _set_quantity_in_stock(cls, location, product, qty=10):
        cls.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }
        ).action_apply_inventory()

    def _check_move_lines(self, picking, move_lines):
        moves = []
        for move in picking.move_ids:
            moves.append((move.product_id, move.product_qty, bool(move.bom_line_id)))
        self.assertEqual(set(moves), set(move_lines))

    def test_split_picking_kit_no_split(self):
        """Check number of kits is equal to the split limit.

        No split is needed.
        """
        picking = self._create_picking()
        self._create_stock_move(self.product_garden_table, picking, qty=3)
        picking.action_confirm()
        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=3)
            new_picking = rc_picking.records
        self.assertFalse(new_picking, "No new picking should be created")
        self.assertAlmostEqual(
            self._get_kit_quantity(picking, self.bom_garden_table),
            3,
            "The number of kits should be 3",
        )

    def test_split_picking_kit_single_split(self):
        """Check number of kits is 4 and the split limit is 3.

        3 kits are split off to a new picking.
        The remaining 1 kit is in the original picking.
        """
        picking = self._create_picking()
        self._create_stock_move(self.product_garden_table, picking, qty=4)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=3)
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "The new picking is confirmed")
        self.assertAlmostEqual(
            self._get_kit_quantity(new_picking, self.bom_garden_table),
            3,
            "3 kits are moved to the new picking",
        )
        self.assertEqual(
            picking.state, "confirmed", "The original picking is confirmed"
        )
        self.assertAlmostEqual(
            self._get_kit_quantity(picking, self.bom_garden_table),
            1,
            "1 kit is left in the original picking",
        )

    def test_split_assigned_picking_kit_single_split(self):
        """Check reservation is decreased if needed.

        Number of kits is 3 and the split limit is 2.

        """
        self._set_quantity_in_stock(
            self.stock_location, self.product_garden_table_leg, qty=12
        )
        self._set_quantity_in_stock(
            self.stock_location, self.product_garden_table_top, qty=3
        )
        picking = self._create_picking()
        self._create_stock_move(self.product_garden_table, picking, qty=3)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self.assertEqual(picking.move_ids.mapped("quantity"), [12.0, 3.0])

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=2)
            new_picking = rc_picking.records

        self.assertEqual(new_picking.state, "assigned", "New picking is assigned")
        self.assertEqual(picking.state, "assigned", "Original picking is assigned")
        self.assertEqual(picking.move_ids.mapped("quantity"), [4.0, 1.0])
        self.assertEqual(new_picking.move_ids.mapped("quantity"), [8.0, 2.0])

    def test_split_picking_kit_with_no_kit(self):
        """Check split picking only has non kit product.

        When splitting non-kit prodicts, we split by quantity.
        """
        picking = self._create_picking()
        move1 = self._create_stock_move(self.product_garden_table_top, picking, qty=3)
        move2 = self._create_stock_move(self.product_garden_table_leg, picking, qty=21)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=7)
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "The new picking is confirmed")
        self._check_move_lines(
            new_picking,
            [
                (self.product_garden_table_top, 3, False),
                (self.product_garden_table_leg, 4, False),
            ],
        )
        self.assertFalse(
            self._get_kit_quantity(new_picking, self.bom_garden_table),
            "No kit in the new picking",
        )
        self.assertEqual(
            move1.picking_id, new_picking, "The first move is moved to the new picking"
        )
        self.assertEqual(
            move2.picking_id,
            picking,
            "The second move is left in the original picking..",
        )
        self.assertAlmostEqual(
            move2.product_uom_qty, 17, "..with the remaining quantity"
        )

    def test_split_picking_with_product_and_kit(self):
        """Check split picking has product and kit products.

        When splitting product and kit products, we split by kit quantity
        and respecting the moves order.
        """
        picking = self._create_picking()
        self._create_stock_move(self.product_garden_table_top, picking, qty=3)
        self._create_stock_move(self.product_garden_table_leg, picking, qty=21)
        move_kit = self._create_stock_move(self.product_garden_table, picking, qty=4)
        move_kit.sequence = 999
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=6)
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "The new picking is confirmed")
        self.assertFalse(
            self._get_kit_quantity(new_picking, self.bom_garden_table),
            msg="No kit is moved because of the order of the moves",
        )
        self._check_move_lines(
            new_picking,
            [
                (self.product_garden_table_top, 3, False),
                (self.product_garden_table_leg, 3, False),
            ],
        )

        self.assertEqual(
            picking.state, "confirmed", "The original picking remains confirmed"
        )
        self._check_move_lines(
            picking,
            [
                (self.product_garden_table_leg, 18, False),
                (self.product_garden_table_top, 4, True),
                (self.product_garden_table_leg, 16, True),
            ],
        )
        self.assertAlmostEqual(
            self._get_kit_quantity(picking, self.bom_garden_table),
            4,
            msg="4 kits are left in the original picking",
        )

    def test_split_picking_with_kit_and_product(self):
        """Check split picking has kit and product products.

        When splitting kit and product products, we split by kit quantity
        and respecting the moves order.
        """
        picking = self._create_picking()
        move_kit = self._create_stock_move(self.product_garden_table, picking, qty=4)
        move_kit.sequence = 1
        self._create_stock_move(self.product_garden_table_top, picking, qty=3)
        self._create_stock_move(self.product_garden_table_leg, picking, qty=21)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="kit_quantity", kit_split_quantity=6)
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "The new picking is confirmed")
        self.assertAlmostEqual(
            self._get_kit_quantity(new_picking, self.bom_garden_table),
            4,
            msg="4 kits are moved to the new picking",
        )
        self._check_move_lines(
            new_picking,
            [
                (self.product_garden_table_top, 4, True),
                (self.product_garden_table_leg, 16, True),
                (self.product_garden_table_top, 2, False),
            ],
        )

        self.assertEqual(
            picking.state, "confirmed", "The original picking remains confirmed"
        )
        self._check_move_lines(
            picking,
            [
                (self.product_garden_table_top, 1, False),
                (self.product_garden_table_leg, 21, False),
            ],
        )
        self.assertFalse(
            self._get_kit_quantity(picking, self.bom_garden_table),
            "No kit is left in the original picking",
        )
