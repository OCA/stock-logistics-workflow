# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingProductLotSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        supplier_location = cls.env.ref("stock.stock_location_suppliers")
        stock_location = cls.env.ref("stock.stock_location_stock")
        picking_type_in = cls.env.ref("stock.picking_type_in")
        picking_type_in.auto_create_lot = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "tracking": "serial",
                "auto_create_lot": True,
            }
        )
        cls.product.lot_sequence_id.write(
            {
                "prefix": "Test/",
                "padding": 5,
                "number_increment": 1,
                "number_next_actual": 1,
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "picking_type_id": picking_type_in.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
            }
        )

    def test_stock_picking_product_lot_sequence(self):
        self.assertTrue(self.product.lot_sequence_id)
        next_serial = self.env["stock.lot"]._get_next_serial(
            self.env.company, self.product
        )
        self.assertRegex(next_serial, r"Test/\d{5}")
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.button_validate()
        for move_line in self.picking.move_line_ids:
            self.assertRegex(move_line.lot_name, r"Test/\d{5}")
