# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, common


class TestPurchaseOrder(common.SavepointCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("base.main_company")
        self.product_storable = self.env["product.product"].create(
            {"name": "Producto Storable", "type": "product"}
        )
        self.partner = self.env["res.partner"].create({"name": "Mr Odoo"})
        self.company.lc_journal_id = self.env["account.journal"].create(
            {
                "name": "Test LC",
                "type": "general",
                "code": "MISC-LC",
                "company_id": self.company.id,
            }
        )

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_storable
        order = order_form.save()
        return order

    def test_order_lc(self):
        order = self._create_purchase_order()
        order.button_confirm()
        self.assertTrue(order.landed_cost_ids)
        picking = order.picking_ids[0]
        picking.move_ids_without_package.quantity_done = 1
        picking.button_validate()
        lc = order.landed_cost_ids[0]
        self.assertTrue(picking in lc.picking_ids)
