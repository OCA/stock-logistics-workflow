# Copyright 2022 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleLineReturnedQty(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 100,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 10
            line_form.price_unit = 1000
        cls.order = order_form.save()

    def _return_picking(self, picking, qty, to_refund=True):
        """Helper method to create a return of the original picking. It could
        be refundable or not"""
        # The return wizard no longer exists on 20.0: the picking builds
        # its own return, which stays in draft.
        return_picking = picking._create_return()
        return_picking.move_ids.write({"product_uom_qty": qty, "to_refund": to_refund})
        return_picking.action_confirm()
        return_picking.action_assign()
        self._validate_picking(return_picking)

    def _validate_picking(self, picking):
        """Helper method to confirm the pickings"""
        for line in picking.move_ids:
            line.quantity = line.product_uom_qty
            line.picked = True
        picking._action_done()

    def test_returned_qty(self):
        self.order.action_confirm()
        so_line = self.order.order_line[0]
        self.assertEqual(so_line.qty_returned, 0.0)
        # Partial delivery one
        picking = self.order.picking_ids
        picking.action_assign()
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(so_line.qty_returned, 0.0)
        # Make a return for 5 units
        self._return_picking(picking, 5.0, to_refund=True)
        self.assertEqual(so_line.qty_returned, 5.0)

    def test_returned_qty_not_done_moves(self):
        self.order.action_confirm()
        so_line = self.order.order_line[0]
        picking = self.order.picking_ids
        picking.action_assign()
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        # Create a return picking without validate it, so the returned qty should be 0
        return_picking = picking._create_return()
        return_picking.move_ids.write({"product_uom_qty": 5.0, "to_refund": True})
        return_picking.action_confirm()
        return_picking.action_assign()
        # Return picking is in assigned state, so the returned qty should be 0
        self.assertEqual(return_picking.state, "assigned")
        # qty_returned should be 0 because the return picking is not done yet
        self.assertEqual(so_line.qty_returned, 0.0)
