# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestBatchInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.batch_model = cls.env["stock.picking.batch"]
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
        cls.invoice_frequency.update({"automatic_batch_invoicing": True})
        cls.sale = cls._create_sale_order(cls.product_test1.ids + cls.product_test2.ids)
        cls.sale.update(
            {
                "invoice_frequency_id": cls.invoice_frequency.id,
            }
        )
        cls.sale2 = cls._create_sale_order(
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

    def test_batch_invoice_no_qty_done(self):
        """Batch invoicing without quantity."""
        (self.sale | self.sale2).action_confirm()
        sale_picking = self.sale.picking_ids[0]
        sale2_picking = self.sale2.picking_ids[0]
        batch = self.batch_model.create(
            {
                "picking_ids": [(6, 0, (sale_picking | sale2_picking).ids)],
            }
        )
        batch.action_confirm()
        batch.action_assign()
        wizard_dict = batch.action_done()
        wizard = Form(
            self.env[(wizard_dict.get("res_model"))].with_context(
                **wizard_dict["context"]
            )
        ).save()
        wizard.process()
        self.assertTrue(self.sale.invoice_ids)
        self.assertFalse(self.sale2.invoice_ids)

    def test_batch_invoice_with_qty_done(self):
        """Batch invoicing with quantity."""
        (self.sale | self.sale2).action_confirm()
        sale_picking = self.sale.picking_ids[0]
        sale2_picking = self.sale2.picking_ids[0]
        batch = self.batch_model.create(
            {
                "picking_ids": [(6, 0, (sale_picking | sale2_picking).ids)],
            }
        )
        batch.action_confirm()
        batch.action_assign()
        batch.move_line_ids.qty_done = 1
        batch.action_done()
        self.assertTrue(self.sale.invoice_ids)
        self.assertFalse(self.sale2.invoice_ids)
