# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestStockPickingGroupByPartnerMonthlyInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env.ref("base.res_partner_1")
        cls.partner1.invoicing_mode = "at_shipping"
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner1.id,
                "partner_invoice_id": cls.partner1.id,
                "partner_shipping_id": cls.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.so2 = cls.so1.copy(
            {"partner_id": cls.partner2.id, "partner_invoice_id": cls.partner2.id}
        )

        cls.env.ref("stock.warehouse0").group_shippings = True
        stock_location = cls.env.ref("stock.stock_location_stock")
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, cls.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": 100,
                            "location_id": stock_location.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def test_one(self):
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.picking = self.so1.picking_ids
        self.assertEqual(self.so1.picking_ids, self.so2.picking_ids)
        self.picking.sale_id = self.so2
        self.assertEqual(len(self.picking.sale_ids), 2)
        for line in self.picking.move_lines:
            line.quantity_done = line.product_uom_qty
        self.picking.action_assign()
        self.picking.with_context(test_queue_job_no_delay=True).button_validate()
        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 0)
