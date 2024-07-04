# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta as td

from odoo.tests import common


class TestStockMoveOriginalDate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pickingModel = cls.env["stock.picking"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.product_1 = cls.env["product.product"].create(
            {"name": "test", "type": "product"}
        )

        cls.comparison_delta = td(seconds=1)
        cls.today = datetime.today()
        cls.tomorrow = cls.today + td(1)
        cls.day_2 = cls.today + td(2)

    @classmethod
    def create_picking_in(cls, product, date_move, qty=10.0):
        picking = cls.pickingModel.create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.stock_location.id,
                        },
                    )
                ],
            }
        )
        return picking

    @classmethod
    def _validate_picking(cls, picking):
        for line in picking.move_lines:
            line.quantity_done = line.product_uom_qty
        picking._action_done()

    def test_01_original_date_stored(self):
        picking = self.create_picking_in(self.product_1, self.tomorrow)
        self.assertTrue(picking.scheduled_date)
        self.assertFalse(picking.original_scheduled_date)
        move = picking.move_lines
        self.assertTrue(move.date)
        self.assertFalse(move.original_date)
        picking.action_confirm()
        self.assertTrue(picking.original_scheduled_date)
        self.assertEqual(picking.scheduled_date, picking.original_scheduled_date)
        self.assertTrue(move.original_date)
        self.assertEqual(move.date, move.original_date)
        move.date = self.day_2
        picking.action_assign()
        self.assertEqual(picking.original_scheduled_date, self.tomorrow)
        self.assertEqual(picking.scheduled_date, self.day_2)
        self.assertEqual(move.original_date, self.tomorrow)
        self.assertEqual(move.date, self.day_2)
        # Validating the picking update `date` (date done now) but not `original_date`
        self._validate_picking(picking)
        self.assertAlmostEqual(
            picking.original_scheduled_date, self.tomorrow, delta=self.comparison_delta
        )
        self.assertAlmostEqual(
            move.original_date, self.tomorrow, delta=self.comparison_delta
        )
        self.assertAlmostEqual(move.date, self.today, delta=self.comparison_delta)
