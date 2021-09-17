# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import timedelta

from odoo import fields
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


# @tagged("-at_install", "post_install")
class TestStockDeferredAssign(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockDeferredAssign, cls).setUpClass()
        cls.StockPicking = cls.env["stock.picking"]
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.categ_all = cls.env.ref("product.product_category_all")
        cls.categ_all.property_cost_method = "average"
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "type": "product",
                "tracking": "none",
                "standard_price": 1,
                "categ_id": cls.categ_all.id,
            }
        )
        StockQuant = cls.env["stock.quant"]
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 2000,
            }
        )

    def create_sale_order(self, commitment_date=False):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "commitment_date": commitment_date,
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
        picking = self.env["stock.picking"].search([("sale_id", "=", sale_order.id)])
        return sale_order, picking

    def test_stock_deferred_assign_at_confirm(self):
        sale_order, picking = self.create_sale_order()
        self.assertEqual(len(picking.move_line_ids), 1)

    def test_stock_deferred_assign_by_date_far(self):
        self.picking_type.reservation_method = "by_date"
        self.picking_type.reservation_days_before = 4
        sale_order, picking = self.create_sale_order("2099-07-06")
        self.assertEqual(len(picking.move_line_ids), 0)
        self.assertEqual(
            picking.move_lines.date_expected,
            fields.Datetime.to_datetime("2099-07-06 00:00:00"),
        )
        self.assertEqual(
            picking.move_lines.reservation_date, fields.Date.to_date("2099-07-02")
        )

    def test_stock_deferred_assign_by_date_near(self):
        self.picking_type.reservation_method = "by_date"
        self.picking_type.reservation_days_before = 4
        commitment_date = fields.Date.today() + timedelta(days=3)
        sale_order, picking = self.create_sale_order(commitment_date)
        self.assertEqual(len(picking.move_line_ids), 1)

    def test_stock_deferred_assign_manual(self):
        self.picking_type.reservation_method = "manual"
        sale_order, picking = self.create_sale_order()
        self.assertEqual(len(picking.move_line_ids), 0)
