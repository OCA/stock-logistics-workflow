# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommonBase


@tagged("post_install", "-at_install")
class TestProcurementGroupCarrier(TestSaleCommonBase):
    # FIXME: TestSale is very heavy and create tons of records w/ no tracking disable
    # for every test. Move to SavepointCase!
    def setUp(self):
        super().setUp()
        self.carrier1 = self.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier",
                "product_id": self.env.ref("delivery.product_product_delivery").id,
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def test_sale_procurement_group_carrier(self):
        """Check the SO procurement group contains the carrier on SO confirmation"""
        product = self.env.ref("product.product_delivery_01")
        sale_order_line_vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "price_unit": product.list_price,
        }
        sale_order_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "carrier_id": self.carrier1.id,
            "order_line": [(0, 0, sale_order_line_vals)],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        so = self.env["sale.order"].create(sale_order_vals)
        so.action_confirm()
        self.assertTrue(so.picking_ids)
        self.assertEqual(so.procurement_group_id.carrier_id, so.carrier_id)
