# Copyright 2021 Daniel Domínguez - https://xtendoo.es
# Copyright 2021 Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests import common


class TestStockReportShowPartner(common.TransactionCase):
    def setUp(self):
        super(TestStockReportShowPartner, self).setUp()
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.partner = self.partner_model.create({"name": "Test partner"})
        self.product = self.product_model.create(
            {"name": "Test product", "type": "product"}
        )

        # Create a SO with a line:
        self.so = self.env["sale.order"].create(
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
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                        },
                    ),
                ],
            }
        )
        # Create a PO with a line:
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                            "date_planned": datetime.today(),
                        },
                    ),
                ],
            }
        )

    def test_stock_move_line_partner_id_like_sale_order_partner_id(self):
        sale_order = self.so
        sale_order.action_confirm()
        picking = sale_order.picking_ids[:1]
        self.assertEqual(
            sale_order.partner_id.id, picking.move_ids_without_package[:1].partner_id.id
        )

    def test_stock_move_line_partner_id_like_purchase_order_partner_id(self):
        purchase_order = self.po
        purchase_order.button_confirm()
        picking = purchase_order.picking_ids[:1]
        self.assertEqual(
            purchase_order.partner_id.id,
            picking.move_line_ids_without_package[:1].partner_id.id,
        )
