# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingSaleOrderLink(TransactionCase):
    def setUp(self):
        super(TestStockPickingSaleOrderLink, self).setUp()
        self.Location = self.env["stock.location"]
        self.PickingType = self.env["stock.picking.type"]
        self.Picking = self.env["stock.picking"]
        self.Product = self.env["product.template"]
        self.warehouse = self.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )

        self.product = self.Product.create(
            {
                "name": "Product - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Customer - test", "customer": True}
        )
        self.picking_type = self.PickingType.search(
            [("warehouse_id", "=", self.warehouse.id), ("code", "=", "outgoing")]
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.product_variant_ids.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 100.00,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        self.picking = self.Picking.search([("sale_id", "=", sale_order.id)])

    def test_picking_to_sale_order(self):
        result = self.picking.action_view_sale_order()
        self.assertEqual(result["res_id"], self.picking.sale_id.id)
