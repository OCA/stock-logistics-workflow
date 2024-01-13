# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestStockMoveFromSaleLine(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 10
            line_form.price_unit = 1000
            line_form.name = "Custom name"
        cls.order = order_form.save()

    def test_stock_move_from_sale_line(self):
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.move_lines.name, "Custom name")
