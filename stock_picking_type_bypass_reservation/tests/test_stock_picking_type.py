# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.picking_type_out = cls.env["stock.picking.type"].browse(
            cls.env["ir.model.data"]._xmlid_to_res_id("stock.picking_type_out")
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _create_picking(self):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "test_out_bypass",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )

    def test_stock_picking_type_no_bypass(self):
        """Check picking is not confirmed if not bypass_reservation without stock"""
        self.picking_type_out.bypass_reservation = False
        picking = self._create_picking()
        picking.action_confirm()
        self.assertEqual(picking.state, "confirmed")
        self.assertFalse(picking.move_line_ids)

    def test_stock_picking_type_bypass(self):
        """Check picking is confirmed if bypass_reservation without stock"""
        self.picking_type_out.bypass_reservation = True
        picking = self._create_picking()
        picking.action_confirm()
        self.assertEqual(picking.state, "assigned")
        self.assertEqual(picking.move_line_ids[0].reserved_uom_qty, 1.0)
