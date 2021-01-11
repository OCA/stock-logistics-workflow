# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import Form, SavepointCase


class TestSaleStockMtoAsMtsOrderpoint(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        ref = cls.env.ref
        cls.partner = ref("base.res_partner_2")
        cls.product = cls.env["product.product"].create(
            {"name": "Test MTO", "type": "product"}
        )
        cls.vendor_partner = ref("base.res_partner_12")
        cls.env["product.supplierinfo"].create(
            {
                "name": cls.vendor_partner.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "min_qty": 1.0,
                "price": 1.0,
            }
        )

        cls.warehouse = ref("stock.warehouse0")

        cls.mto_route = ref("stock.route_warehouse0_mto")
        cls.buy_route = ref("purchase_stock.route_warehouse0_buy")
        cls.product.write({"route_ids": [(6, 0, [cls.mto_route.id, cls.buy_route.id])]})

    @classmethod
    def _create_sale_order(cls):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        sale_form.warehouse_id = cls.warehouse
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 1
        return sale_form.save()

    def test_mto_as_mts_orderpoint(self):
        order = self._create_sale_order()
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertFalse(orderpoint)
        order.action_confirm()
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id)]
        )

        self.assertEqual(
            orderpoint.location_id,
            self.warehouse._get_locations_for_mto_orderpoints(),
        )
        self.assertAlmostEqual(orderpoint.product_min_qty, 0.0)
        self.assertAlmostEqual(orderpoint.product_max_qty, 0.0)
        self.product.write({"route_ids": [(5, 0, 0)]})
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertFalse(orderpoint)
        orderpoint = (
            self.env["stock.warehouse.orderpoint"]
            .with_context(active_test=False)
            .search([("product_id", "=", self.product.id)])
        )
        self.assertTrue(orderpoint)

    def test_cancel_sale_order_orderpoint(self):
        order = self._create_sale_order()
        order.action_confirm()
        order.action_cancel()
        order.action_draft()
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_confirm_mto_as_mts_sudo_needed(self):
        """Check access right needed to confirm sale.

        A sale manager user with no right on inventory will raise an access
        right error on confirmation.
        This is the why of the sudo in `sale_stock_mto_as_mts_orderpoint`
        """
        user = self.env.ref("base.user_demo")
        sale_group = self.env.ref("sales_team.group_sale_manager")
        sale_group.users = [(4, user.id)]
        order = self._create_sale_order()
        order.with_user(user).action_confirm()
