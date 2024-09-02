# Copyright 2020 Iryna Vyshnevska Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class StockPickingReturnLotTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_obj = cls.env["stock.picking"]
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "product", "tracking": "lot"}
        )
        cls.lot_1 = cls.env["stock.lot"].create(
            {"name": "000001", "product_id": cls.product.id}
        )
        cls.lot_2 = cls.env["stock.lot"].create(
            {"name": "000002", "product_id": cls.product.id}
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 1, lot_id=cls.lot_1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 2, lot_id=cls.lot_2
        )
        cls.picking = cls.picking_obj.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 3,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.action_set_quantities_to_reservation()
        cls.picking._action_done()

    @classmethod
    def create_return_wiz(cls, picking):
        return (
            cls.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )

    def _create_validate_picking(self):
        picking = self.picking_obj.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                ],
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.action_set_quantities_to_reservation()
        picking._action_done()
        return picking

    def test_partial_return(self):
        wiz = self.create_return_wiz(self.picking)
        wiz._onchange_picking_id()
        self.assertEqual(len(wiz.product_return_moves), 2)
        return_line_1 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_1: m.lot_id == lot
        )
        return_line_2 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_2: m.lot_id == lot
        )
        self.assertEqual(return_line_1.quantity, 1)
        self.assertEqual(return_line_2.quantity, 2)
        return_line_2.quantity = 1
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.picking_obj.browse(picking_returned_id)
        move_1 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_1: m.restrict_lot_id == lot
        )
        move_2 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_2: m.restrict_lot_id == lot
        )
        self.assertEqual(move_1.move_line_ids.lot_id, self.lot_1)
        self.assertEqual(move_2.move_line_ids.lot_id, self.lot_2)
        self.assertEqual(move_2.product_qty, 1)

    def test_full_return_after_partial_return(self):
        self.test_partial_return()
        wiz = self.create_return_wiz(self.picking)
        wiz._onchange_picking_id()
        self.assertEqual(len(wiz.product_return_moves), 2)

        return_line_1 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_1: m.lot_id == lot
        )
        return_line_2 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_2: m.lot_id == lot
        )
        self.assertEqual(return_line_1.quantity, 0)
        self.assertEqual(return_line_2.quantity, 1)
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.picking_obj.browse(picking_returned_id)
        move_1 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_1: m.restrict_lot_id == lot
        )
        move_2 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_2: m.restrict_lot_id == lot
        )
        self.assertFalse(move_1)
        self.assertEqual(move_2.move_line_ids.lot_id, self.lot_2)
        self.assertEqual(move_2.product_qty, 1)

    def test_multiple_move_same_product_different_lot(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 1, lot_id=self.lot_1
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 1, lot_id=self.lot_2
        )
        picking = self._create_validate_picking()
        wiz = self.create_return_wiz(picking)
        wiz._onchange_picking_id()
        self.assertEqual(len(wiz.product_return_moves), 2)
        return_line_1 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_1: m.lot_id == lot
        )
        return_line_2 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_2: m.lot_id == lot
        )
        self.assertEqual(return_line_1.quantity, 1)
        self.assertEqual(return_line_2.quantity, 1)
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.picking_obj.browse(picking_returned_id)
        move_1 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_1: m.restrict_lot_id == lot
        )
        move_2 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_2: m.restrict_lot_id == lot
        )
        self.assertEqual(move_1.move_line_ids.lot_id, self.lot_1)
        self.assertEqual(move_2.move_line_ids.lot_id, self.lot_2)
        self.assertEqual(move_2.product_qty, 1)

    def test_multiple_move_same_product_same_lot(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 2, lot_id=self.lot_1
        )
        picking = self._create_validate_picking()
        wiz = self.create_return_wiz(picking)
        wiz._onchange_picking_id()
        self.assertEqual(len(wiz.product_return_moves), 1)
        return_line_1 = wiz.product_return_moves.filtered(
            lambda m, lot=self.lot_1: m.lot_id == lot
        )
        self.assertEqual(return_line_1.quantity, 2)
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.picking_obj.browse(picking_returned_id)
        move_1 = picking_returned.move_ids.filtered(
            lambda m, lot=self.lot_1: m.restrict_lot_id == lot
        )
        self.assertEqual(move_1.move_line_ids.lot_id, self.lot_1)
        self.assertEqual(move_1.product_qty, 2)
