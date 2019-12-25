# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestStockMoveQuickLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveQuickLot, cls).setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product for test", "type": "product", "tracking": "lot"}
        )
        cls.env["stock.move"].create(
            {
                "name": "a move",
                "product_id": cls.product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.picking.action_assign()
        cls.move_line = cls.picking.move_lines[:1]

    def test_quick_input(self):
        self.assertTrue(self.move_line)
        with self.assertRaises(ValidationError):
            self.move_line.onchange_line_lot_name()
        self.move_line.line_lot_name = "SN99999999999"
        self.move_line._compute_line_lot_name()
        self.move_line.onchange_line_lot_name()  # Try again
        self.move_line.life_date = "2030-12-31"
        lot = self.move_line.move_line_ids[:1].lot_id
        self.assertTrue(lot)
        self.move_line.line_lot_name = False
        self.move_line.line_lot_name = "SN99999999998"
        lot2 = self.move_line.move_line_ids[:1].lot_id
        self.assertNotEqual(lot, lot2)
        self.move_line.life_date = False
        self.move_line.life_date = "2030-12-28"
        self.assertEqual(str(lot2.life_date), "2030-12-28 00:00:00")
