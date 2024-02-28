# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestPickingInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_test1 = cls._create_product("Product Test 1", cls.uom_unit)
        cls.product_test2 = cls._create_product("Product Test 2", cls.uom_kg)
        cls.product_test3 = cls._create_product("Product Test 3", cls.uom_unit)
        cls.product_test4 = cls._create_product("Product Test 4", cls.uom_kg)
        cls.invoice_frequency = cls.env.ref(
            "sale_invoice_frequency.sale_invoice_frequency_daily"
        )
        cls.invoice_frequency.update({"automatic_picking_invoicing": True})
        cls.sale_inv_freq = cls._create_sale_order(
            cls.product_test1.ids + cls.product_test2.ids
        )
        cls.sale_inv_freq.update(
            {
                "invoice_frequency_id": cls.invoice_frequency.id,
            }
        )
        cls.sale_no_inv_freq = cls._create_sale_order(
            cls.product_test3.ids + cls.product_test4.ids
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_test1, cls.stock_loc, 10.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_test2, cls.stock_loc, 10.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_test3, cls.stock_loc, 10.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_test4, cls.stock_loc, 10.0
        )

    @classmethod
    def _create_product(cls, name, uom_id):
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "uom_id": uom_id.id,
                "uom_po_id": uom_id.id,
            }
        )

    @classmethod
    def _create_sale_order(cls, product_ids):
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id,
                            "product_uom_qty": 1,
                        },
                    )
                    for product_id in product_ids
                ],
            }
        )

    def test_picking_invoice_with_auto_invoice(self):
        """Picking automatic invoicing."""
        self.sale_inv_freq.action_confirm()
        for picking in self.sale_inv_freq.picking_ids.sorted("id"):
            picking.action_assign()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()
        self.assertTrue(self.sale_inv_freq.invoice_ids)

    def test_picking_invoice_without_auto_invoice(self):
        """Picking non automatic invoicing."""
        self.sale_no_inv_freq.action_confirm()
        for picking in self.sale_no_inv_freq.picking_ids.sorted("id"):
            picking.action_assign()
            picking.action_set_quantities_to_reservation()
            picking.button_validate()
        self.assertFalse(self.sale_no_inv_freq.invoice_ids)
