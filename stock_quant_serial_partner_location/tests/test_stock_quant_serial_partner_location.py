# Copyright 2024 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestStockQuantSerialPartnerLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "serial product",
                "tracking": "serial",
                "type": "product",
            }
        )
        cls.lot_id = cls.env["stock.production.lot"].create(
            {
                "name": "test lot",
                "product_id": cls.product.id,
            }
        )

    def test_sending_twice_same_serial_number(self):

        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 1,
                "lot_id": self.lot_id.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "test move",
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.write({"qty_done": 1.0})
        move._action_done()
        self.assertEqual(move.state, "done")
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 1,
                "lot_id": self.lot_id.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "test move",
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.write({"qty_done": 1.0})
        move._action_done()
        self.assertEqual(move.state, "done")

    def test_same_behaviour_in_regular_locations(self):
        with self.assertRaises(ValidationError):
            self.env["stock.quant"].create(
                {
                    "product_id": self.product.id,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "quantity": 2,
                    "lot_id": self.lot_id.id,
                }
            )
