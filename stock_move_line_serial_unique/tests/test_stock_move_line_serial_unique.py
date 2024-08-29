# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockQuantSerialUnique(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.vendor_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.owner = cls.env["res.partner"].create({"name": "test owner"})
        cls.product = cls.env["product.product"].create(
            {"name": "test product", "type": "product", "tracking": "serial"}
        )
        cls.serial1 = cls.env["stock.lot"].create(
            {
                "company_id": cls.env.company.id,
                "product_id": cls.product.id,
                "name": "001",
            }
        )
        cls.serial2 = cls.env["stock.lot"].create(
            {
                "company_id": cls.env.company.id,
                "product_id": cls.product.id,
                "name": "002",
            }
        )
        # Create stock for serial '001'.
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "lot_id": cls.serial1.id,
                "quantity": 1,
            }
        )

    def _create_picking(self, location, location_dest, picking_type, owner):
        picking_vals = {
            "picking_type_id": picking_type.id,
            "location_id": location.id,
            "location_dest_id": location_dest.id,
            "owner_id": owner.id,
        }
        return self.env["stock.picking"].create(picking_vals)

    def _create_moveline(self, product, picking):
        move_line_vals = {
            "product_id": product.id,
            "picking_id": picking.id,
            "quantity": 1,
        }
        return self.env["stock.move.line"].create(move_line_vals)

    def test_picking_in_serial_with_stock(self):
        self.assertEqual(self.picking_type_in.use_create_lots, True)
        picking_in = self._create_picking(
            self.vendor_location, self.stock_location, self.picking_type_in, self.owner
        )
        moveline = self._create_moveline(self.product, picking_in)
        # Stock exists for serial '001'.
        with self.assertRaises(ValidationError):
            moveline.write({"lot_name": "001"})

    def test_picking_in_serials_with_and_without_stock(self):
        picking_in = self._create_picking(
            self.vendor_location, self.stock_location, self.picking_type_in, self.owner
        )
        moveline = self._create_moveline(self.product, picking_in)
        # Stock does not exist for serial '002'.
        moveline.write({"lot_name": "002"})
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "lot_id": self.serial2.id,
                "quantity": 1,
            }
        )
        picking_in.action_confirm()
        # Now stock exists for serial '002'.
        with self.assertRaises(ValidationError):
            picking_in.button_validate()
        # Stock does not exist for serial '003'.
        moveline.write({"lot_name": "003"})
        picking_in.button_validate()

    def test_picking_out_serial_with_stock(self):
        self.assertEqual(self.picking_type_out.use_create_lots, False)
        picking_out = self._create_picking(
            self.stock_location,
            self.vendor_location,
            self.picking_type_out,
            self.owner,
        )
        moveline = self._create_moveline(self.product, picking_out)
        # Stock exists for serial '001' but no check should be done
        # for outgoing/internal moves.
        moveline.write({"lot_id": self.serial1.id})
        picking_out.action_confirm()
        picking_out.button_validate()
