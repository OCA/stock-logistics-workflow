# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class StockPickingReturnRestrictedQtyTest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        product = cls.env["product.product"].create(
            {"name": "test_product", "type": "product"}
        )
        picking_type_out = cls.env.ref("stock.picking_type_out")
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 20,
                            "product_uom": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.move_ids[:1].quantity = 20
        cls.picking.button_validate()

    def get_return_picking_wizard(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return stock_return_picking_form.save()

    def test_return_not_allowed(self):
        """On this test we create a return picking with more quantity
        than the quantity that client have on his hand"""
        self.picking.picking_type_id.restrict_return_qty = True
        return_picking = self.get_return_picking_wizard(self.picking)
        self.assertEqual(return_picking.product_return_moves.quantity, 20)
        return_picking.product_return_moves.quantity = 30
        with self.assertRaises(UserError):
            return_picking._create_returns()

    def test_return_without_restriction(self):
        """On this test we create a return picking with more quantity
        than the quantity that client have on his hand
        without the quantity restriction"""
        self.picking.picking_type_id.restrict_return_qty = False
        return_picking = self.get_return_picking_wizard(self.picking)
        self.assertEqual(return_picking.product_return_moves.quantity, 20)
        return_picking.product_return_moves.quantity = 30
        return_picking._create_returns()
        self.assertEqual(return_picking.product_return_moves.quantity, 30)

    def test_multiple_return(self):
        """On this test we are going to follow a sequence that a client
        can follow if he tries to return a product"""
        self.picking.picking_type_id.restrict_return_qty = True
        wiz = self.get_return_picking_wizard(self.picking)
        wiz.product_return_moves.quantity = 10
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.env["stock.picking"].browse(picking_returned_id)

        wiz = self.get_return_picking_wizard(self.picking)
        self.assertEqual(wiz.product_return_moves.quantity, 10)

        picking_returned._action_done()
        wiz = self.get_return_picking_wizard(self.picking)
        self.assertEqual(wiz.product_return_moves.quantity, 10)

        wiz.product_return_moves.quantity = 80
        with self.assertRaises(UserError):
            wiz.product_return_moves._onchange_quantity()

    def test_multiple_return_without_restriction(self):
        """On this test we are going to follow a sequence that a client
        can follow if he tries to return a product
        without the quantity restriction"""
        self.picking.picking_type_id.restrict_return_qty = False
        wiz = self.get_return_picking_wizard(self.picking)
        wiz.product_return_moves.quantity = 10
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.env["stock.picking"].browse(picking_returned_id)

        wiz = self.get_return_picking_wizard(self.picking)
        self.assertEqual(wiz.product_return_moves.quantity, 10)

        picking_returned._action_done()
        wiz = self.get_return_picking_wizard(self.picking)
        self.assertEqual(wiz.product_return_moves.quantity, 10)

        wiz.product_return_moves.quantity = 80
        wiz.product_return_moves._onchange_quantity()
        self.assertEqual(wiz.product_return_moves.quantity, 80)

    def _create_picking(self, picking_type, location, location_dest, product, qty):
        return self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "location_id": location.id,
                            "location_dest_id": location_dest.id,
                        },
                    )
                ],
            }
        )

    def _validate(self, picking):
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = picking.move_ids.product_uom_qty
        picking.button_validate()

    def _return(self, picking, qty):
        wiz = self.get_return_picking_wizard(picking)
        wiz.product_return_moves.quantity = qty
        return_picking = self.env["stock.picking"].browse(wiz._create_returns()[0])
        self._validate(return_picking)
        return return_picking

    def _create_chained_receipt_and_delivery(self):
        """Receipt whose move is chained to a delivery move (as with MTO)."""
        product = self.env["product.product"].create(
            {"name": "test_chained_product", "type": "product"}
        )
        supplier_location = self.env.ref("stock.stock_location_suppliers")
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        picking_type_in = self.env.ref("stock.picking_type_in")
        picking_type_in.restrict_return_qty = True
        receipt = self._create_picking(
            picking_type_in, supplier_location, stock_location, product, 10
        )
        delivery = self._create_picking(
            self.env.ref("stock.picking_type_out"),
            stock_location,
            customer_location,
            product,
            10,
        )
        delivery.move_ids.move_orig_ids = receipt.move_ids
        self._validate(receipt)
        self._validate(delivery)
        return receipt, delivery

    def test_return_chained_move_consumed(self):
        """Goods received and delivered through a chained move can't be
        returned to the vendor."""
        receipt, _delivery = self._create_chained_receipt_and_delivery()
        wiz = self.get_return_picking_wizard(receipt)
        self.assertEqual(wiz.product_return_moves.quantity, 0)
        wiz.product_return_moves.quantity = 10
        with self.assertRaises(UserError):
            wiz._create_returns()

    def test_return_chained_move_returned_back(self):
        """Goods delivered through a chained move and returned by the
        customer can be returned to the vendor."""
        receipt, delivery = self._create_chained_receipt_and_delivery()
        self._return(delivery, 4)
        wiz = self.get_return_picking_wizard(receipt)
        self.assertEqual(wiz.product_return_moves.quantity, 4)
        wiz.product_return_moves.quantity = 5
        with self.assertRaises(UserError):
            wiz._create_returns()
        wiz.product_return_moves.quantity = 4
        wiz._create_returns()

    def test_return_chained_move_returned_back_and_redelivered(self):
        """Goods returned by the customer and delivered again are not
        available to be returned to the vendor."""
        receipt, delivery = self._create_chained_receipt_and_delivery()
        customer_return = self._return(delivery, 4)
        self._return(customer_return, 3)
        wiz = self.get_return_picking_wizard(receipt)
        self.assertEqual(wiz.product_return_moves.quantity, 1)
