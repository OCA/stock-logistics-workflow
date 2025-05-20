# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestBatchPrintPickings(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.client_1 = cls.env["res.partner"].create({"name": "Client 1"})
        cls.picking_client_1 = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type.id,
                "partner_id": cls.client_1.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": cls.productA.name,
                "product_id": cls.productA.id,
                "product_uom_qty": 10,
                "product_uom": cls.productA.uom_id.id,
                "picking_id": cls.picking_client_1.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

        cls.client_2 = cls.env["res.partner"].create({"name": "Client 2"})
        cls.picking_client_2 = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type.id,
                "partner_id": cls.client_2.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": cls.productB.name,
                "product_id": cls.productB.id,
                "product_uom_qty": 10,
                "product_uom": cls.productA.uom_id.id,
                "picking_id": cls.picking_client_2.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.batch = cls.env["stock.picking.batch"].create(
            {
                "name": "Batch 1",
                "company_id": cls.env.company.id,
            }
        )

    def test_stock_picking_batch_print_pickings_01(self):
        """Picking type with unchecked print pickings from batch."""
        self.picking_type.print_documents_from_batch = False
        self.batch.update(
            {
                "picking_ids": [
                    (6, 0, (self.picking_client_1 | self.picking_client_2).ids)
                ]
            }
        )
        with self.assertRaises(UserError):
            self.batch.action_print_pickings()

    def test_stock_picking_batch_print_pickings_02(self):
        """Picking type with checked print pickings
        from batch but with 0 copies to print."""
        self.picking_type.print_documents_from_batch = "pickings"
        self.picking_type.number_copies_pickings = 0
        self.batch.update(
            {
                "picking_ids": [
                    (6, 0, (self.picking_client_1 | self.picking_client_2).ids)
                ]
            }
        )
        with self.assertRaises(UserError):
            self.batch.action_print_pickings()

    def test_stock_picking_batch_print_pickings_03(self):
        """Picking type with checked print pickings from batch and copies to print
        but batch without pickings."""
        self.picking_type.print_documents_from_batch = "pickings"
        self.picking_type.number_copies_pickings = 2
        with self.assertRaises(UserError):
            self.batch.action_print_pickings()

    def test_stock_picking_batch_print_pickings_04(self):
        """Picking type with checked print pickings from batch, copies to print
        and batch with pickings."""
        self.picking_type.print_documents_from_batch = "pickings"
        self.picking_type.number_copies_pickings = 2
        self.batch.update(
            {
                "picking_ids": [
                    (6, 0, (self.picking_client_1 | self.picking_client_2).ids)
                ]
            }
        )
        result = self.batch.action_print_pickings()
        if (
            result.get("xml_id", False)
            and result["xml_id"] == "web.action_base_document_layout_configurator"
        ):
            result = result.get("context", {}).get("report_action", {})
        self.assertEqual(result.get("type"), "ir.actions.report")
        report_name = result.get("report_name")
        self.assertEqual(
            result.get("report_name"),
            "stock_picking_batch_print_pickings.report_picking_batch_print_pickings",
        )
        report_pdf = self.env["ir.actions.report"]._render(report_name, self.batch.ids)
        self.assertGreaterEqual(len(report_pdf[0]), 1)
        self.assertEqual(str(report_pdf[0]).count(self.picking_client_1.name), 2)
        self.assertEqual(str(report_pdf[0]).count(self.picking_client_2.name), 2)
