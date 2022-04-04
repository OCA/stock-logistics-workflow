# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta
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

    def _create_quant(self, lot=None, qty=1):
        """Create any number of quants.

        :param lot: create quants with these lot(s).
        When None, create lots on the fly.
        When empty recordset, create quants without lot.
        :param qty: number of quants to create. If more than one lot is
        passed, the number of lots overrides this.
        """
        if lot and len(lot) > qty:
            qty = len(lot)
        quants = self.env["stock.quant"]
        for i in range(0, qty):
            if lot and len(lot) > 0:
                use_lot = lot[i]
            elif lot is None:
                use_lot = self._create_lot()
            else:
                use_lot = lot
            quants += self.env["stock.quant"].create(
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "location_id": self.location.id,
                    "lot_id": use_lot.id,
                }
            )
        return quants

    def _create_picking(self, qty=1, confirm=True, assign=True):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.location.id,
                "location_dest_id": self.dest_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "testmove",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": qty,
                        },
                    )
                ],
            }
        )
        if confirm:
            picking.action_confirm()
            if assign:
                picking.action_assign()
        return picking

    def _backdate_moves(self):
        """Moves are selected for reassignment based on their write dates"""
        for move in self.env["stock.move"].search([]):
            move.write_date -= timedelta(minutes=1)

    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Tracked product",
                "tracking": "serial",
                "type": "product",
            }
        )
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.picking_type.use_manual_lot_selection = True
        self.location = self.env.ref("stock.stock_location_stock")
        self.dest_location = self.env.ref("stock.stock_location_customers")

    def test_01_force_manual_selection(self):
        """Picking can not be validated without manual lot selection"""
        lot = self._create_quant().lot_id
        picking = self._create_picking()
        picking.move_line_ids.qty_done = picking.move_line_ids.product_qty
        with self.assertRaisesRegex(
                UserError, "Serial"
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            picking.button_validate()
        picking.move_line_ids.manual_lot_id = lot
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            self.env["stock.quant"]
            .search(
                [
                    ("location_id", "=", self.dest_location.id),
                    ("product_id", "=", self.product.id),
                ]
            )
            .mapped("lot_id"),
            lot,
        )

    def test_02_reassign_reservation(self):
        """Pickings are rereserved after their lots were fetched on another"""
        quant1 = self._create_quant()
        picking = self._create_picking()
        self.assertEqual(quant1.reserved_quantity, 1)
        quant2 = self._create_quant()
        picking2 = self._create_picking()
        self.assertEqual(quant2.reserved_quantity, 1)
        self.assertEqual(picking2.move_line_ids.lot_id, quant2.lot_id)
        self.assertTrue(picking.move_line_ids)
        self._backdate_moves()
        picking2.write({
            "move_line_ids": [
                (1, picking2.move_line_ids.id, {
                    "manual_lot_id": quant1.lot_id.id,
                })]})
        self.assertTrue(picking.move_line_ids)
        self.assertEqual(picking.move_line_ids.lot_id, quant2.lot_id)
        with self.assertRaises(
            UserError
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            picking.button_validate()
        self.assertEqual(
            picking.move_lines.product_qty, picking.move_line_ids.product_qty
        )
        picking.move_line_ids.update(
            dict(
                qty_done=picking.move_line_ids.product_qty,
                manual_lot_id=quant2.lot_id,
            )
        )
        quant_domain = [
            ("location_id", "=", self.dest_location.id),
            ("product_id", "=", self.product.id),
        ]
        self.assertFalse(self.env["stock.quant"].search(quant_domain))
        picking.button_validate()
        self.assertEqual(
            self.env["stock.quant"].search(quant_domain).lot_id, quant2.lot_id
        )

    def test_03_multiple_lines_flip(self):
        """Multiple lines (with each other's lots) can be reassigned at once.
        """
        quant1, quant2 = self._create_quant(qty=2)
        picking = self._create_picking(2)
        self.assertEqual(quant1.reserved_quantity, 1)
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
        self.assertEqual(quant1.reserved_quantity, 1)
        self.assertEqual(quant2.reserved_quantity, 1)
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

    def test_04_multiple_lines_move_lot(self):
        """
        Test that moving a manual lot from one line to the other works
        """
        self._create_quant(qty=2)
        picking = self._create_picking(2)
        line_with_lot, line_without_lot = picking.move_line_ids
        lot1 = line_with_lot.lot_id
        line_with_lot.manual_lot_id = lot1
        picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': lot1.id,
                }),
                (1, line_with_lot.id, {
                    'manual_lot_id': False,
                }),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, lot1)
        other_line = picking.move_line_ids - line_without_lot
        self.assertTrue(other_line.lot_id)
        self.assertFalse(other_line.manual_lot_id)
        self.assertEqual(other_line.product_qty, 1)

    def test_05_multiple_lines_assign(self):
        """
        Test that just reassigning a manual lot from one line to the other works
        """
        self._create_quant(qty=2)
        picking = self._create_picking(2)
        line_with_lot, line_without_lot = picking.move_line_ids
        lot1 = line_with_lot.lot_id
        line_with_lot.manual_lot_id = lot1
        picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': line_with_lot.manual_lot_id.id,
                }),
                # this is what the webclient sends when we don't change
                # the line
                (4, line_with_lot.id, False),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, lot1)
        other_line = picking.move_line_ids - line_without_lot
        self.assertTrue(other_line.lot_id)
        self.assertFalse(other_line.manual_lot_id)
        self.assertEqual(other_line.product_qty, 1)

    def test_06_multiple_lines_delete(self):
        """
        Test that reassigning a manual lot from one line to the other works
        when deleting the first one
        """
        self._create_quant(qty=2)
        picking = self._create_picking(2)
        line_with_lot, line_without_lot = picking.move_line_ids
        lot1 = line_with_lot.lot_id
        line_with_lot.manual_lot_id = lot1
        picking.write({
            'move_line_ids': [
                (1, line_without_lot.id, {
                    'manual_lot_id': line_with_lot.manual_lot_id.id,
                }),
                (2, line_with_lot.id, False),
            ],
        })
        self.assertEqual(line_without_lot.lot_id, lot1)
        self.assertFalse(line_with_lot.exists())

    def test_07_serial_not_in_stock(self):
        """It is not allowed to assign a serial that is not in stock"""
        self._create_quant()
        picking = self._create_picking()
        with self.assertRaisesRegex(UserError, "than you have in stock"):
            picking.move_line_ids.manual_lot_id = self._create_lot()

    def test_08_backorder(self):
        """An assigned move line on a picking can be left untransferred."""
        picking = self._create_picking(confirm=False)
        line = picking.move_lines
        # Create up to 4 lines
        line.copy()
        line.copy()
        line.copy()
        self._create_quant(qty=3)
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
        lot1, lot2 = self._create_quant(qty=2).mapped("lot_id")
        picking = self._create_picking()
        self.product.tracking = 'none'
        picking.do_unreserve()
        picking.action_assign()
        self.assertTrue(picking.move_line_ids.manual_lot_id)
        self.assertEqual(
            picking.move_line_ids.manual_lot_id,
            picking.move_line_ids.lot_id)
        # Lot is synced with manual lot
        picking.move_line_ids.manual_lot_id = lot2
        self.assertEqual(picking.move_line_ids.lot_id, lot2)
        # Manual lot is synced with lot
        picking.move_line_ids.lot_id = lot1
        self.assertEqual(picking.move_line_ids.manual_lot_id, lot1)
        # Unsetting the serial raises if there is stock without serial.
        with self.assertRaisesRegex(
                UserError, "than you have in stock"
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            picking.move_line_ids.manual_lot_id = False

        # Create stock without serial. Serial can now be unset
        self._create_quant(self.env["stock.production.lot"])
        picking.move_line_ids.manual_lot_id = False
        self.assertFalse(picking.move_line_ids.lot_id)
        self.assertTrue(picking.move_line_ids.product_qty)

        picking.move_line_ids.qty_done = (
            picking.move_line_ids.product_qty
        )
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_10_unset_manual_lot(self):
        """Unsetting a manual lot does not unreserve the move line."""
        lot1 = self._create_quant(qty=2).mapped("lot_id")[0]
        picking = self._create_picking()
        ml = picking.move_line_ids
        ml.qty_done = ml.product_qty
        picking.move_line_ids.manual_lot_id = lot1
        picking.move_line_ids.manual_lot_id = False
        self.assertEqual(ml.product_qty, 1)
        with self.assertRaisesRegex(
                UserError, "Serial"
        ), self.env.clear_upon_failure(), self.env.cr.savepoint():
            picking.button_validate()
        picking.move_line_ids.manual_lot_id = lot1
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_11_no_manual_selection(self):
        """Manual lot is kept in sync with lot.

        Also, picking can be validated if manual lot is not set.
        """
        lot2 = self._create_quant(qty=2).mapped("lot_id")[1]
        picking = self._create_picking()
        self.picking_type.use_manual_lot_selection = False
        ml = picking.move_line_ids
        ml.qty_done = ml.product_qty
        picking.move_line_ids.lot_id = lot2
        self.assertEqual(picking.move_line_ids.manual_lot_id, lot2)
        picking.move_line_ids.manual_lot_id = False
        self.assertEqual(picking.move_line_ids.lot_id, lot2)
        self.assertFalse(picking.move_line_ids.manual_lot_id)
        self.assertEqual(picking.move_line_ids.lot_id, lot2)
        picking.move_line_ids.qty_done = (
            picking.move_line_ids.product_qty)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_line_ids.manual_lot_id, lot2)

    def test_12_no_overassignment(self):
        """Overassignment does not occur after assigning manual lots.

        This problem can occur when pickings are reassigned before the values
        for stock.move.line's product_qty are stored in the database.
        """
        self._create_quant(qty=2)
        picking = self._create_picking(3)
        self._create_quant(qty=5)
        picking2 = self._create_picking(3)
        self.assertEqual(picking.move_lines.state, "partially_available")
        self.assertEqual(len(picking.move_line_ids), 2)
        self.assertEqual(picking2.move_lines.state, "assigned")
        self._backdate_moves()
        picking2.write({
            "move_line_ids_without_package": [
                (
                    1, picking2.move_line_ids[0].id,
                    {"manual_lot_id": picking.move_line_ids[0].lot_id.id}
                ),
                (
                    1, picking2.move_line_ids[1].id,
                    {"manual_lot_id": picking.move_line_ids[1].lot_id.id}
                ),
            ],
        })
        self.assertEqual(len(picking.move_line_ids), 3)
        self.assertEqual(picking.move_lines.state, "assigned")
        self.assertEqual(len(picking2.move_line_ids), 3)
        self.assertEqual(picking2.move_lines.state, "assigned")

    def test_13_reassign_multiple(self):
        """This specific reassignment breaks if product_qty is not up to date.

        Having two assigned pickings with a quantity of two, assigning a lot
        from the first picking to the first picking while assigning the
        original lot from the assigned move line to the second move line of
        the same picking should not raise an error.
        """
        self._create_quant(qty=4)
        picking = self._create_picking(2)
        picking2 = self._create_picking(2)
        self._backdate_moves()
        vals = [
            (1, picking2.move_line_ids[0].id,
             {"manual_lot_id": picking.move_line_ids[0].lot_id.id}),
            (1, picking2.move_line_ids[1].id,
             {"manual_lot_id": picking2.move_line_ids[0].lot_id.id}),
        ]
        picking2.write({"move_line_ids_without_package": vals})
        self.assertEqual(len(picking.move_line_ids), 2)
        self.assertEqual(picking.move_lines.state, "assigned")
        self.assertEqual(len(picking2.move_line_ids), 2)
        self.assertEqual(picking2.move_lines.state, "assigned")
