# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingBatchActualDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "standard_price": 100.0,
            }
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_location, 100.0
        )

    def create_picking(self):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "10 out",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.product_1.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": picking.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": self.product_1.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "qty_done": 10.0,
                "picking_id": picking.id,
                "product_uom_id": self.product_1.uom_id.id,
            }
        )
        return picking

    def test_stock_picking_batch_actual_date(self):
        delivery_1 = self.create_picking()
        delivery_2 = self.create_picking()
        delivery_3 = self.create_picking()
        batch_picking = self.env["stock.picking.batch"].create(
            {
                "actual_date": date(2025, 5, 5),
                "picking_ids": [Command.set([delivery_1.id, delivery_2.id])],
            }
        )
        self.assertEqual(batch_picking.actual_date, date(2025, 5, 5))
        self.assertEqual(delivery_1.actual_date, date(2025, 5, 5))
        self.assertEqual(delivery_2.actual_date, date(2025, 5, 5))
        batch_picking.picking_ids = [Command.set([delivery_1.id, delivery_3.id])]
        self.assertEqual(delivery_1.actual_date, date(2025, 5, 5))
        self.assertEqual(delivery_2.actual_date, False)
        self.assertEqual(delivery_3.actual_date, date(2025, 5, 5))
        batch_picking.actual_date = date(2025, 5, 1)
        self.assertEqual(delivery_1.actual_date, date(2025, 5, 1))
        self.assertEqual(delivery_3.actual_date, date(2025, 5, 1))
        delivery_1.actual_date = date(2025, 5, 3)
        batch_picking.action_confirm()
        self.assertEqual(delivery_1.actual_date, date(2025, 5, 3))
        batch_picking.action_done()
        self.assertEqual(delivery_1.actual_date, date(2025, 5, 1))

    def test_detached_picking_actual_date_reset(self):
        delivery_1 = self.create_picking()
        delivery_2 = self.create_picking()
        batch_picking = self.env["stock.picking.batch"].create(
            {
                "actual_date": date(2025, 5, 5),
                "picking_ids": [Command.set([delivery_1.id, delivery_2.id])],
            }
        )
        batch_picking.action_confirm()
        move_line_1 = batch_picking.move_line_ids.filtered(
            lambda l: l.picking_id.id == delivery_1.id
        )
        move_line_1.qty_done = 0
        batch_picking.action_done()
        self.assertFalse(delivery_1.actual_date)
        self.assertEqual(delivery_2.actual_date, date(2025, 5, 5))
