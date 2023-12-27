# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form, SavepointCase


class TestSalePurchaseStockLineNote(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True
        cls.sale_note = "Custom sale note"

    @classmethod
    def _create_sale_order(cls):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 100
            line_form.route_id = cls.mto_route
            line_form.note = cls.sale_note
        return sale_form.save()

    def test_create_move(self):
        sale = self._create_sale_order()
        sale.action_confirm()
        delivery_move = sale.order_line.move_ids
        self.assertEqual(delivery_move.sale_note, self.sale_note)

    def test_purchase_line(self):
        sale = self._create_sale_order()
        sale.action_confirm()
        purchase_order = sale._get_purchase_orders()
        self.assertEqual(purchase_order.order_line.sale_note, self.sale_note)
