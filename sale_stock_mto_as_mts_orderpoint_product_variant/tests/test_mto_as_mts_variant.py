# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from odoo.addons.stock_product_variant_mto.tests.common import TestMTOVariantCommon


class TestMtoAsMtsVariant(TestMTOVariantCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.vendor_partner = cls.env.ref("base.res_partner_12")
        cls.env["product.supplierinfo"].create(
            [
                {
                    "name": cls.vendor_partner.id,
                    "product_tmpl_id": variant.product_tmpl_id.id,
                    "product_id": variant.id,
                    "min_qty": 1.0,
                    "price": 1.0,
                }
                for variant in cls.variants_pen
            ]
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.mto_as_mts = True

    @classmethod
    def setUpClassProduct(cls):
        super().setUpClassProduct()
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.template_pen.write(
            {"route_ids": [(6, 0, [cls.buy_route.id, cls.mto_route.id])]}
        )

    @classmethod
    def _create_sale_order(cls, products):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        sale_form.warehouse_id = cls.warehouse
        for product in products:
            with sale_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 1
        return sale_form.save()

    def _get_orderpoint_for_products(self, products, archived=False):
        orderpoint = self.env["stock.warehouse.orderpoint"]
        if archived:
            orderpoint = orderpoint.with_context(active_test=False)
        return orderpoint.search([("product_id", "in", products.ids)])

    def test_mto_as_mts_orderpoint_warehouse_archive(self):
        black_pen = self.black_pen
        order = self._create_sale_order(black_pen)
        order.action_confirm()
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertTrue(orderpoint)
        self.warehouse.mto_as_mts = False
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertFalse(orderpoint)

    def test_mto_as_mts_orderpoint_product_archive(self):
        black_pen = self.black_pen
        order = self._create_sale_order(black_pen)
        order.action_confirm()
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertTrue(orderpoint)
        self.toggle_is_mto(black_pen)
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertFalse(orderpoint)

    def test_mto_as_mts_orderpoint(self):
        black_pen = self.black_pen
        blue_pen = self.blue_pen
        red_pen = self.red_pen
        green_pen = self.green_pen
        order = self._create_sale_order(black_pen)
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertFalse(orderpoint)
        self.assertIn(self.mto_route, black_pen.route_ids)
        self.assertTrue(black_pen.is_mto)
        order.action_confirm()
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertTrue(orderpoint)
        self.assertEqual(
            orderpoint.location_id,
            self.warehouse._get_locations_for_mto_orderpoints(),
        )
        self.assertAlmostEqual(orderpoint.product_min_qty, 0.0)
        self.assertAlmostEqual(orderpoint.product_max_qty, 0.0)
        # Setting the black pen to mto should drop its orderpoint
        self.toggle_is_mto(black_pen)
        orderpoint = self._get_orderpoint_for_products(black_pen)
        self.assertFalse(orderpoint)
        # Creating and confirming an order for variants should create
        # an orderpoint for all variants but the black pen
        order = self._create_sale_order(self.variants_pen)
        order.action_confirm()
        # black pen orderpoint is archived
        self.assertFalse(self._get_orderpoint_for_products(black_pen))
        self.assertTrue(self._get_orderpoint_for_products(black_pen, archived=True))
        other_pens = red_pen | green_pen | blue_pen
        self.assertEqual(len(self._get_orderpoint_for_products(other_pens)), 3)

    def test_mtp_as_mts_orderpoint_product_no_mto(self):
        self.assertIn(self.buy_route, self.template_pen.route_ids)
        template_pen = self.template_pen
        black_pen = self.black_pen
        variants_pen = self.variants_pen
        self.assertIn(self.buy_route, black_pen.route_ids)
        # set everything to not mto
        template_pen.write({"route_ids": [(3, self.mto_route.id, 0)]})
        self.assertIn(self.buy_route, black_pen.route_ids)
        self.assertNotIn(self.mto_route, black_pen.route_ids)
        self.toggle_is_mto(variants_pen)
        self.assertIn(self.mto_route, black_pen.route_ids)
        self.assertIn(self.buy_route, black_pen.route_ids)
        self.toggle_is_mto(variants_pen)
        self.assertNotIn(self.mto_route, black_pen.route_ids)
        self.assertIn(self.buy_route, black_pen.route_ids)
        # then check that no orderpoint is created
        order = self._create_sale_order(black_pen)
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", black_pen.id)]
        )
        self.assertFalse(orderpoint)
        order.action_confirm()
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [("product_id", "=", black_pen.id)]
        )
        self.assertFalse(orderpoint)

    def test_cancel_sale_order_orderpoint(self):
        order = self._create_sale_order(self.variants_pen)
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
        order = self._create_sale_order(self.variants_pen)
        order.with_user(user).action_confirm()
