# Copyright 2022 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, common


class TestSaleLineReturnedQtyMrp(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        route_manufacture = cls.warehouse.manufacture_pull_id.route_id
        route_mto = cls.warehouse.mto_pull_id.route_id
        route_buy = cls.warehouse.buy_pull_id.route_id
        dropshipping_route = cls.env["stock.location.route"].create(
            {
                "name": "Dropship",
                "sale_selectable": True,
                "product_selectable": True,
                "product_categ_selectable": True,
            }
        )
        # Create dropship product
        cls.dropship_product_main = cls.env["product.product"].create(
            {"name": "Large Desk"}
        )
        vendor1 = cls.env["res.partner"].create({"name": "vendor1"})
        seller1 = cls.env["product.supplierinfo"].create(
            {
                "name": vendor1.id,
                "price": 8,
            }
        )
        seller2 = cls.env["product.supplierinfo"].create(
            {
                "name": vendor1.id,
                "price": 8,
            }
        )

        # Create Kit product
        cls.product = cls.env["product.product"].create(
            {
                "name": "test kit",
                "type": "product",
                "route_ids": [(6, 0, [route_manufacture.id, route_mto.id])],
            }
        )
        cls.c1 = cls.env["product.product"].create(
            {"name": "test component 1", "type": "product"}
        )
        cls.c2 = cls.env["product.product"].create(
            {"name": "test component 2", "type": "product"}
        )
        cls.c3 = cls.env["product.product"].create(
            {
                "name": "test component 3",
                "type": "product",
                "route_ids": [
                    (6, 0, [dropshipping_route.id, route_mto.id, route_buy.id])
                ],
                "seller_ids": [(6, 0, [seller1.id])],
            }
        )
        cls.c4 = cls.env["product.product"].create(
            {
                "name": "test component 4",
                "type": "product",
                "route_ids": [
                    (6, 0, [dropshipping_route.id, route_mto.id, route_buy.id])
                ],
                "seller_ids": [(6, 0, [seller2.id])],
            }
        )
        # Create BoM
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_qty": 1,
                "type": "phantom",
            }
        )
        # Create bom lines
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.c1.id, "product_qty": 1}
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.bom.id, "product_id": cls.c2.id, "product_qty": 1}
        )

        # Create dropshipping BoM
        cls.dropship_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.dropship_product_main.product_tmpl_id.id,
                "product_id": cls.dropship_product_main.id,
                "product_qty": 1,
                "type": "phantom",
            }
        )
        # Create bom lines
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.dropship_bom.id, "product_id": cls.c3.id, "product_qty": 1}
        )
        cls.env["mrp.bom.line"].create(
            {"bom_id": cls.dropship_bom.id, "product_id": cls.c4.id, "product_qty": 1}
        )

        # Add components stock
        cls.env["stock.quant"].create(
            {
                "product_id": cls.c1.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 100,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.c2.id,
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

        # create dropship order
        dropship_order_form = Form(cls.env["sale.order"])
        dropship_order_form.partner_id = cls.partner
        with dropship_order_form.order_line.new() as line_form:
            line_form.product_id = cls.dropship_product_main
            line_form.product_uom_qty = 10
            line_form.price_unit = 1000
        cls.dropship_order = dropship_order_form.save()

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

    def test_01_returned_qty(self):
        self.order.action_confirm()
        so_line = self.order.order_line[0]
        self.assertEqual(so_line.qty_returned, 0.0)
        # Deliver the order
        picking = self.order.picking_ids
        self.assertEqual(len(picking.move_lines), 2)
        picking.action_assign()
        self._validate_picking(picking)
        self.assertEqual(so_line.qty_returned, 0.0)
        # Make a return for 5 of the 10 units delivered
        self._return_picking(picking, 5.0, to_refund=True)
        self.assertEqual(so_line.qty_returned, 5.0)

    def test_02_returned_qty(self):
        self.dropship_order.action_confirm()
        po = self.env["purchase.order"].search(
            [("group_id", "=", self.dropship_order.procurement_group_id.id)]
        )
        po.button_confirm()
        so_line = self.dropship_order.order_line[0]
        self.assertEqual(so_line.qty_returned, 0.0)
        # Deliver the order
        picking = self.dropship_order.picking_ids
        self.assertEqual(len(picking.move_lines), 2)
        picking.action_assign()
        self._validate_picking(picking)
        self.assertEqual(so_line.qty_returned, 0.0)
        self._return_picking(picking, 5.0, to_refund=True)
        self.assertEqual(so_line.qty_returned, 5.0)
