# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockPickingPurchaseOrderLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location_obj = cls.env["stock.location"]
        cls.stock_picking_type_obj = cls.env["stock.picking.type"]
        cls.stock_picking_obj = cls.env["stock.picking"]
        cls.product_product_obj = cls.env["product.product"]
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )
        cls.product = cls.product_product_obj.create(
            {
                "name": "product_template_obj - Test",
                "type": "consu",
                "standard_price": 100.00,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Vendor - test"})
        cls.picking_type = cls.stock_picking_type_obj.search(
            [("warehouse_id", "=", cls.warehouse.id), ("code", "=", "incoming")]
        )
        purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_qty": 1.0,
                            "product_uom": cls.product.uom_po_id.id,
                            "price_unit": 10.0,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        cls.picking = cls.stock_picking_obj.search(
            [("purchase_id", "=", purchase_order.id)]
        )

    def test_picking_to_purchase_order(self):
        result = self.picking.action_view_purchase_order()
        self.assertEqual(result["res_id"], self.picking.purchase_id.id)
