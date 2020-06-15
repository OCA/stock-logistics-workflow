# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestStockPickingPurchaseOrderLink(TransactionCase):
    def setUp(self):
        super(TestStockPickingPurchaseOrderLink, self).setUp()
        self.stock_location_obj = self.env["stock.location"]
        self.stock_picking_type_obj = self.env["stock.picking.type"]
        self.stock_picking_obj = self.env["stock.picking"]
        self.product_product_obj = self.env["product.product"]
        self.warehouse = self.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )

        self.product = self.product_product_obj.create(
            {
                "name": "product_template_obj - Test",
                "type": "product",
                "standard_price": 100.00,
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Vendor - test", "vendor": True}
        )
        self.picking_type = self.stock_picking_type_obj.search(
            [("warehouse_id", "=", self.warehouse.id), ("code", "=", "incoming")]
        )
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 10.0,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.picking = self.stock_picking_obj.search(
            [("purchase_id", "=", purchase_order.id)]
        )

    def test_picking_to_sale_order(self):
        result = self.picking.action_view_purchase_order()
        self.assertEqual(result["res_id"], self.picking.purchase_id.id)
