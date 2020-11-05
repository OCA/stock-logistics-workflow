# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestStockPickingAutoCreateLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lot_obj = cls.env["stock.production.lot"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})
        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Product Serial Test",
                "type": "product",
                "tracking": "serial",
                "auto_create_lot": True,
            }
        )
        cls.product_serial_not_auto = cls.env["product.product"].create(
            {
                "name": "Product Serial Not Auto Test",
                "type": "product",
                "tracking": "serial",
                "auto_create_lot": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "product",
                "tracking": "lot",
                "auto_create_lot": True,
            }
        )
        cls.picking = (
            cls.env["stock.picking"]
            .with_context(default_picking_type_id=cls.picking_type_in.id)
            .create(
                {
                    "partner_id": cls.supplier.id,
                    "picking_type_id": cls.picking_type_in.id,
                    "location_id": cls.supplier_location.id,
                }
            )
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-auto-serial",
                "product_id": cls.product_serial.id,
                "picking_id": cls.picking.id,
                "picking_type_id": cls.picking_type_in.id,
                "product_uom_qty": 3.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.picking_type_in.default_location_dest_id.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-not-auto-serial",
                "product_id": cls.product_serial_not_auto.id,
                "picking_id": cls.picking.id,
                "picking_type_id": cls.picking_type_in.id,
                "product_uom_qty": 4.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.picking_type_in.default_location_dest_id.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-auto-lot",
                "product_id": cls.product.id,
                "picking_id": cls.picking.id,
                "picking_type_id": cls.picking_type_in.id,
                "product_uom_qty": 2.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.picking_type_in.default_location_dest_id.id,
            }
        )

    def test_auto_create_lot(self):
        self.picking_type_in.auto_create_lot = True
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial)
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto)
        self.assertTrue(move.display_assign_serial)

        # Assign manual serials
        for line in move.move_line_ids:
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)
