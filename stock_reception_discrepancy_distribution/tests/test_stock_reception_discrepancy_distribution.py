# Copyright 2023 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, common


class TestStockReceptionDiscrepancyDistribution(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        # activate MTO route
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True

        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "product",
                "route_ids": [(6, 0, (mto_route + buy_route).ids)],
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "test - supplier"})
        cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_po_id.id,
                "price": 500.00,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "test - partner2"})
        cls.order = cls._create_sale_order(cls.partner, qty_ordered=10.0)
        cls.order2 = cls._create_sale_order(cls.partner2, qty_ordered=15.0)

    @classmethod
    def _create_sale_order(cls, partner, qty_ordered):
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = qty_ordered
            line_form.price_unit = 1000
        return order_form.save()

    def test_stock_reception_discrepancy_distribution(self):
        self.order.action_confirm()
        self.order2.action_confirm()
        # A purchase order must has been created
        purchase_order = self.order._get_purchase_orders()
        purchase_order.button_approve()
        picking_in = purchase_order.picking_ids
        # we will receipt 30.00 units instead of 25.00
        picking_in.move_lines.quantity_done = 30.0

        # Test action
        action = picking_in.move_lines.action_change_move_dest_qty()
        self.assertFalse(action["res_id"])
        self.assertEqual(picking_in.move_lines.id, action["context"]["default_move_id"])

        # Test workflow
        wiz = Form(
            self.env["stock.reception.discrepancy.distribution.wiz"].with_context(
                **action["context"]
            )
        )
        self.assertEqual(len(wiz.move_dest_ids), 2)

        # Initial wizard values
        self.assertEqual(wiz.move_qty_done, 30.00)
        self.assertEqual(wiz.move_dest_demand, 25.00)
        self.assertEqual(wiz.over_quantity, 5.00)

        # Change values in wizard lines
        with wiz.move_dest_ids.edit(0) as line:
            line.product_uom_qty = 20.0
        with wiz.move_dest_ids.edit(1) as line:
            line.product_uom_qty = 40.0

        self.assertEqual(wiz.move_qty_done, 30.00)
        self.assertEqual(wiz.move_dest_demand, 60.00)
        self.assertEqual(wiz.over_quantity, -30.00)
