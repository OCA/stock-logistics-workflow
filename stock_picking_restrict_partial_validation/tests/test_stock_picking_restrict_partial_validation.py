# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockPickingRestrictPartialValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Picking = cls.env["stock.picking"]
        cls.Quant = cls.env["stock.quant"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type = cls.warehouse.int_type_id
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.shelf_location = cls.env["stock.location"].create(
            {
                "name": "Test Shelf",
                "location_id": cls.stock_location.id,
                "usage": "internal",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test Kit Component", "is_storable": True}
        )
        cls.picking_type.write({"restrict_partial_validation": True})

    @classmethod
    def _create_picking(cls, qty):
        picking = cls.Picking.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.shelf_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": qty,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.shelf_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        return picking

    def test_block_validation_when_not_reserved(self):
        picking = self._create_picking(5)
        self.assertNotEqual(picking.state, "assigned")
        with self.assertRaisesRegex(UserError, "fully reserved"):
            picking.button_validate()

    def test_block_forced_quantities_without_stock(self):
        picking = self._create_picking(5)
        self.assertNotEqual(picking.state, "assigned")
        picking.move_ids.write({"quantity": 5, "picked": True})
        self.assertEqual(picking.state, "assigned")
        with self.assertRaisesRegex(UserError, "physically available"):
            picking.button_validate()

    def test_validate_fully_reserved_and_processed(self):
        self.Quant._update_available_quantity(self.product, self.stock_location, 5)
        picking = self._create_picking(5)
        self.assertEqual(picking.state, "assigned")
        picking.move_ids.write({"picked": True})
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertFalse(picking.backorder_ids)

    def test_block_partial_validation(self):
        self.Quant._update_available_quantity(self.product, self.stock_location, 5)
        picking = self._create_picking(5)
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids.write({"quantity": 3})
        picking.move_ids.write({"picked": True})
        with self.assertRaisesRegex(UserError, "processed in full"):
            picking.button_validate()
        self.assertNotEqual(picking.state, "done")
        self.assertFalse(picking.backorder_ids)

    def test_block_partially_picked_moves(self):
        self.Quant._update_available_quantity(self.product, self.stock_location, 5)
        product_2 = self.env["product.product"].create(
            {"name": "Test Kit Component 2", "is_storable": True}
        )
        self.Quant._update_available_quantity(product_2, self.stock_location, 5)
        picking = self._create_picking(5)
        picking.move_ids = [
            Command.create(
                {
                    "name": product_2.name,
                    "product_id": product_2.id,
                    "product_uom_qty": 5,
                    "product_uom": product_2.uom_id.id,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.shelf_location.id,
                }
            )
        ]
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        picking.move_ids[0].write({"picked": True})
        with self.assertRaisesRegex(UserError, "processed in full"):
            picking.button_validate()
        self.assertFalse(picking.backorder_ids)

    def test_block_partially_picked_lines(self):
        self.Quant._update_available_quantity(self.product, self.stock_location, 5)
        picking = self._create_picking(5)
        self.assertEqual(picking.state, "assigned")
        line = picking.move_line_ids[0]
        line.write({"quantity": 4})
        line.copy({"quantity": 1})
        line.write({"picked": True})
        with self.assertRaisesRegex(UserError, "processed in full"):
            picking.button_validate()
        self.assertFalse(picking.backorder_ids)

    def test_partial_validation_allowed_without_restriction(self):
        self.picking_type.write({"restrict_partial_validation": False})
        self.Quant._update_available_quantity(self.product, self.stock_location, 5)
        picking = self._create_picking(5)
        picking.move_line_ids.write({"quantity": 3})
        picking.move_ids.write({"picked": True})
        res = picking.button_validate()
        self.assertEqual(res.get("res_model"), "stock.backorder.confirmation")
        wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(**res["context"])
            .create({})
        )
        wizard.process()
        self.assertEqual(picking.state, "done")
        self.assertTrue(picking.backorder_ids)
