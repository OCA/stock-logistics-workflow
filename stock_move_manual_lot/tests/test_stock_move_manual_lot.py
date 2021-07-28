# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveManualLot(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Tracked product",
                "tracking": "serial",
                "type": "product",
            }
        )
        self.lot1 = self.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": self.product.id,
            }
        )
        self.lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "product_id": self.product.id,
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "testmove",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        self.picking.picking_type_id.use_manual_lot_selection = True
        self.quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "quantity": 1,
                "location_id": self.picking.location_id.id,
                "lot_id": self.lot1.id,
            }
        )
        self.picking.action_assign()
        self.quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "quantity": 1,
                "location_id": self.picking.location_id.id,
                "lot_id": self.lot2.id,
            }
        )

    def test_force_manual_selection(self):
        self.picking.move_line_ids.qty_done = self.picking.move_line_ids.product_qty
        with self.assertRaises(
            UserError
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            self.picking.button_validate()
        self.picking.move_line_ids.manual_lot_id = self.lot1
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(
            self.env["stock.quant"]
            .search(
                [
                    ("location_id", "=", self.picking.location_dest_id.id),
                    ("product_id", "=", self.product.id),
                ]
            )
            .mapped("lot_id"),
            self.lot1,
        )

    def test_reassign_reservation(self):
        picking2 = self.picking.copy()
        picking2.action_assign()
        self.assertEqual(picking2.move_line_ids.lot_id, self.lot2)
        self.assertTrue(self.picking.move_line_ids)
        picking2.move_line_ids.manual_lot_id = self.lot1
        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(self.picking.move_line_ids.lot_id, self.lot2)
        with self.assertRaises(
            UserError
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            self.picking.button_validate()
        self.assertEqual(
            self.picking.move_lines.product_qty, self.picking.move_line_ids.product_qty
        )
        self.picking.move_line_ids.update(
            dict(
                qty_done=self.picking.move_line_ids.product_qty,
                manual_lot_id=self.lot2,
            )
        )
        quant_domain = [
            ("location_id", "=", self.picking.location_dest_id.id),
            ("product_id", "=", self.product.id),
        ]
        self.assertFalse(self.env["stock.quant"].search(quant_domain))
        self.picking.button_validate()
        self.assertEqual(
            self.env["stock.quant"].search(quant_domain).mapped("lot_id"), self.lot2
        )
