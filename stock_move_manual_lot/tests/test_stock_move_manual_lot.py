# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from uuid import uuid1
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveManualLot(TransactionCase):
    def _create_lot(self):
        return self.env["stock.production.lot"].create(
            {
                "name": str(uuid1()),
                "product_id": self.product.id,
            }
        )

    def _create_quant(self, lot):
        return self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "quantity": 1,
                "location_id": self.picking.location_id.id,
                "lot_id": lot.id,
            }
        )

    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Tracked product",
                "tracking": "serial",
                "type": "product",
            }
        )
        self.lot1 = self._create_lot()
        self.lot2 = self._create_lot()
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
        self.quant1 = self._create_quant(self.lot1)
        self.picking.action_assign()
        self.quant2 = self._create_quant(self.lot2)

    def test_01_force_manual_selection(self):
        """Picking can not be validated without manual lot selection"""
        self.picking.move_line_ids.qty_done = self.picking.move_line_ids.product_qty
        with self.assertRaisesRegex(
                UserError, "Serial"
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

    def test_02_reassign_reservation(self):
        """Pickings are rereserved after their lots were fetched on another"""
        self.assertEqual(self.quant1.reserved_quantity, 1)
        picking2 = self.picking.copy()
        self.assertFalse(self.quant2.reserved_quantity, 1)
        picking2.action_assign()
        self.assertEqual(self.quant2.reserved_quantity, 1)
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

    def test_03_multiple_lines_flip(self):
        """Multiple lines (with each other's lots) can be reassigned at once.
        """
        self.picking.action_cancel()
        picking = self.picking.copy()
        picking.move_lines.product_uom_qty = 2
        picking.action_assign()
        move_line1, move_line2 = picking.move_line_ids
        lot1 = move_line1.lot_id
        lot2 = move_line2.lot_id
        picking.write({
            "move_line_ids": [
                (1, picking.move_line_ids[1].id, {"manual_lot_id": lot1.id}),
            ],
        })
        picking.write({
            "move_line_ids": [
                (1, picking.move_line_ids[0].id, {"manual_lot_id": lot1.id}),
                (1, picking.move_line_ids[1].id, {"manual_lot_id": False}),
            ],
        })
        picking.write({
            "move_line_ids": [
                (1, picking.move_line_ids[0].id, {"manual_lot_id": False}),
                (1, picking.move_line_ids[1].id, {"manual_lot_id": lot1.id}),
            ],
        })
        picking.write({
            "move_line_ids": [
                (1, picking.move_line_ids[0].id, {"manual_lot_id": lot2.id}),
                (1, picking.move_line_ids[1].id, {"manual_lot_id": lot1.id}),
            ],
        })
        self.assertEqual(self.quant1.reserved_quantity, 1)
        self.assertEqual(self.quant2.reserved_quantity, 1)
        self.assertTrue(picking.move_line_ids[0].lot_id)
        self.assertTrue(picking.move_line_ids[1].lot_id)
        self.assertEqual(
            picking.move_line_ids.mapped("lot_id"), lot1 + lot2)
        self.assertEqual(picking.move_line_ids[0].product_uom_qty, 1)
        self.assertEqual(picking.move_line_ids[1].product_uom_qty, 1)
        picking.move_line_ids[0].qty_done = picking.move_line_ids[0].product_qty
        picking.move_line_ids[1].qty_done = picking.move_line_ids[1].product_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def _setup_multiple_lines(self):
        """
        Replace self.picking with a picking with multiple lines, where one
        line has a manual lot set
        """
        self.picking.action_cancel()
        self.picking = self.picking.copy()
        self.picking.move_lines.product_uom_qty = 2
        self.picking.action_confirm()
        self.picking.action_assign()
        line_with_lot = self.picking.move_line_ids[0]
        line_with_lot.manual_lot_id = self.lot1
        line_without_lot = self.picking.move_line_ids[1]
        return line_with_lot, line_without_lot

    def test_04_multiple_lines_move_lot(self):
        """
        Test that moving a manual lot from one line to the other works
        """
        line_with_lot, line_without_lot = self._setup_multiple_lines()
        self.picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': line_with_lot.manual_lot_id.id,
                }),
                (1, line_with_lot.id, {
                    'manual_lot_id': False,
                }),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, self.lot1)
        other_line = self.picking.move_line_ids - line_without_lot
        self.assertTrue(other_line.lot_id)
        self.assertFalse(other_line.manual_lot_id)
        self.assertEqual(other_line.product_qty, 1)

    def test_05_multiple_lines_assign(self):
        """
        Test that just reassigning a manual lot from one line to the other works
        """
        line_with_lot, line_without_lot = self._setup_multiple_lines()
        self.picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': line_with_lot.manual_lot_id.id,
                }),
                # this is what the webclient sends when we don't change
                # the line
                (4, line_with_lot.id, False),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, self.lot1)
        other_line = self.picking.move_line_ids - line_without_lot
        self.assertTrue(other_line.lot_id)
        self.assertFalse(other_line.manual_lot_id)
        self.assertEqual(other_line.product_qty, 1)

    def test_06_multiple_lines_delete(self):
        """
        Test that reassigning a manual lot from one line to the other works
        when deleting the first one
        """
        line_with_lot, line_without_lot = self._setup_multiple_lines()
        self.picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': line_with_lot.manual_lot_id.id,
                }),
                (2, line_with_lot.id, False),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, self.lot1)
        self.assertFalse(line_with_lot.exists())

    def test_07_serial_not_in_stock(self):
        """It is not allowed to assign a serial that is not in stock"""
        lot3 = self.env["stock.production.lot"].create({
            "name": "lot3",
            "product_id": self.product.id,
        })
        with self.assertRaisesRegex(UserError, "than you have in stock"):
            self.picking.move_line_ids.manual_lot_id = lot3

    def test_08_backorder(self):
        """An assigned move line on a picking can be left untransferred."""
        self.picking.action_cancel()
        picking = self.picking.copy()
        line = picking.move_lines
        # Create up to 4 lines
        line.copy()
        line.copy()
        line.copy()
        self._create_quant(self._create_lot())
        picking.action_assign()
        # Of the 4 lines, 3 are assigned.
        ml1, ml2, ml3 = picking.move_line_ids
        # We're transferring only the first move line
        ml1.qty_done = ml1.product_qty
        ml1.manual_lot_id = ml1.lot_id
        # 2nd move line is assigned a manual lot, but the 3rd one is not
        ml2.manual_lot_id = ml2.lot_id
        res = picking.button_validate()
        self.env[res["res_model"]].browse(res["res_id"]).process()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)])
        self.assertEqual(backorder.move_lines.product_uom_qty, 3)
        self.assertEqual(backorder.move_lines.reserved_availability, 2)

    def test_09_non_tracked_product(self):
        """Non tracked product, but having lots in stock

        Manual lot is synced with lot_id automatically. If the manual lot
        is unset, reservation of stock without serial is enforced.
        """
        self.product.tracking = 'none'
        self.picking.do_unreserve()
        self.picking.action_assign()
        self.assertTrue(self.picking.move_line_ids.manual_lot_id)
        self.assertEqual(
            self.picking.move_line_ids.manual_lot_id,
            self.picking.move_line_ids.lot_id)
        # Lot is synced with manual lot
        self.picking.move_line_ids.manual_lot_id = self.lot2
        self.assertEqual(self.picking.move_line_ids.lot_id, self.lot2)
        # Manual lot is synced with lot
        self.picking.move_line_ids.lot_id = self.lot1
        self.assertEqual(self.picking.move_line_ids.manual_lot_id, self.lot1)
        # Unsetting the serial raises if there is stock without serial.
        with self.assertRaisesRegex(
                UserError, "than you have in stock"
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            self.picking.move_line_ids.manual_lot_id = False

        # Create stock without serial. Serial can now be unset
        self._create_quant(self.env["stock.production.lot"])
        self.picking.move_line_ids.manual_lot_id = False
        self.assertFalse(self.picking.move_line_ids.lot_id)
        self.assertTrue(self.picking.move_line_ids.product_qty)

        self.picking.move_line_ids.qty_done = (
            self.picking.move_line_ids.product_qty
        )
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")

    def test_10_unset_manual_lot(self):
        """Unsetting a manual lot does not unreserve the move line."""
        ml = self.picking.move_line_ids
        ml.qty_done = ml.product_qty
        self.picking.move_line_ids.manual_lot_id = self.lot1
        self.picking.move_line_ids.manual_lot_id = False
        self.assertEqual(ml.product_qty, 1)
        with self.assertRaisesRegex(
                UserError, "Serial"
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            self.picking.button_validate()
        self.picking.move_line_ids.manual_lot_id = self.lot1
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")

    def test_11_no_manual_selection(self):
        """Manual lot is kept in sync with lot.

        Also, picking can be validated if manual lot is not set.
        """
        self.picking.picking_type_id.use_manual_lot_selection = False
        ml = self.picking.move_line_ids
        ml.qty_done = ml.product_qty
        self.picking.move_line_ids.lot_id = self.lot2
        self.assertEqual(self.picking.move_line_ids.manual_lot_id, self.lot2)
        self.picking.move_line_ids.manual_lot_id = False
        self.assertEqual(self.picking.move_line_ids.lot_id, self.lot2)
        self.assertFalse(self.picking.move_line_ids.manual_lot_id)
        self.assertEqual(self.picking.move_line_ids.lot_id, self.lot2)
        self.picking.move_line_ids.qty_done = (
            self.picking.move_line_ids.product_qty)
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.picking.move_line_ids.manual_lot_id, self.lot2)
