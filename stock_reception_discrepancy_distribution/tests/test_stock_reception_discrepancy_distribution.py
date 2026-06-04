# Copyright 2023 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import Command
from odoo.tests import Form, common


class TestStockReceptionDiscrepancyDistribution(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set((mto_route + buy_route).ids)],
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "test - supplier"})
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
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
        purchase_order = self.order._get_purchase_orders()
        purchase_order.button_approve()
        picking_in = purchase_order.picking_ids
        # we will receipt 30.00 units instead of 25.00
        picking_in.move_ids.quantity = 30.0
        picking_in.move_ids.picked = True
        action = picking_in.move_ids.action_change_move_dest_qty()
        self.assertFalse(action["res_id"])
        self.assertEqual(picking_in.move_ids.id, action["context"]["default_move_id"])
        wiz = Form(
            self.env["stock.reception.discrepancy.distribution.wiz"].with_context(
                **action["context"]
            )
        )
        self.assertEqual(len(wiz.move_dest_ids), 2)
        self.assertEqual(wiz.move_qty_done, 30.00)
        self.assertEqual(wiz.move_dest_demand, 25.00)
        self.assertEqual(wiz.over_quantity, 5.00)
        with wiz.move_dest_ids.edit(0) as line:
            line.product_uom_qty = 20.0
        with wiz.move_dest_ids.edit(1) as line:
            line.product_uom_qty = 40.0
        self.assertEqual(wiz.move_qty_done, 30.00)
        self.assertEqual(wiz.move_dest_demand, 60.00)
        self.assertEqual(wiz.over_quantity, -30.00)

    def test_action_confirm_bumps_demand_on_over_receipt(self):
        self.order.action_confirm()
        self.order2.action_confirm()
        purchase_order = self.order._get_purchase_orders()
        purchase_order.button_approve()
        receipt_move = purchase_order.picking_ids.move_ids
        receipt_move.quantity = 30.0
        receipt_move.picked = True
        wiz = self.env["stock.reception.discrepancy.distribution.wiz"].create(
            {"move_id": receipt_move.id}
        )
        wiz.action_confirm()
        self.assertEqual(receipt_move.product_uom_qty, 30.0)
