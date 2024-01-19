from odoo.tests import Form
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger


class TestStockRuleBuyCheckStockBefore(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_4")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.dropship_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.product.route_ids = [(4, cls.dropship_route.id, 0)]

        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.env.ref("base.res_partner_3").id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_code": "SUPP1",
                "delay": 1,
            }
        )
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with mute_logger("odoo.tests.common.onchange"):
            with sale_form.order_line.new() as line:
                line.product_id = cls.product
                line.product_uom_qty = 1
        cls.sale = sale_form.save()

    def test_flag_off_dropship_normal_behaviour(self):
        """Check normal dropship behaviour with available stock.

        Flag is not set, so even with available quantity a purchase order
        is being created.
        """
        self.dropship_route.rule_ids.disable_if_stock_exists = False
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 3
        )
        self.sale.action_confirm()
        self.assertTrue(self.sale.purchase_order_count == 1)
        self.assertFalse(self.sale.picking_ids)

    def test_flag_on_with_available_quantity(self):
        """Check dropship is bypassed when product is available in the stock."""
        self.dropship_route.rule_ids.disable_if_stock_exists = True
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 3
        )
        self.sale.action_confirm()
        self.assertTrue(self.sale.purchase_order_count == 0)
        self.assertTrue(self.sale.picking_ids)

    def test_flag_on_no_available_quantity(self):
        """Check dropship is activated when the product is not available in stock."""
        self.dropship_route.rule_ids.disable_if_stock_exists = True
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 0
        )
        self.sale.action_confirm()
        self.assertTrue(self.sale.purchase_order_count == 1)
        self.assertFalse(self.sale.picking_ids)
