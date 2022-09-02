# Copyright 2022 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, common


class TestSaleLineReturnedQty(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "product"}
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
        return_wiz_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return_wiz = return_wiz_form.save()
        return_wiz.product_return_moves.quantity = qty
        return_wiz.product_return_moves.to_refund = to_refund
        res = return_wiz.create_returns()
        return_picking = self.env["stock.picking"].browse(res["res_id"])
        self._validate_picking(return_picking)

    def _validate_picking(self, picking):
        """Helper method to confirm the pickings"""
        for line in picking.move_lines:
            line.quantity_done = line.product_uom_qty
        picking._action_done()

    def test_returned_qty(self):
        self.order.action_confirm()
        so_line = self.order.order_line[0]
        self.assertEqual(so_line.qty_returned, 0.0)
        # Partial delivery one
        picking = self.order.picking_ids
        picking.action_assign()
        picking.move_lines.quantity_done = 10.0
        picking._action_done()
        self.assertEqual(so_line.qty_returned, 0.0)
        # Make a return for 5 units
        self._return_picking(picking, 5.0, to_refund=True)
        self.assertEqual(so_line.qty_returned, 5.0)
