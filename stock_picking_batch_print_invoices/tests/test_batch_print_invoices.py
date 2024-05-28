# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


import itertools

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestBatchPrintInvoices(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "invoice_policy": "order",
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "invoice_policy": "delivery",
            }
        )
        cls.client_1 = cls.env["res.partner"].create({"name": "Client 1"})
        cls.sale_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.client_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.productA.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.sale_1.action_confirm()
        cls.picking_1 = cls.sale_1.picking_ids[0]
        context = {
            "active_model": "sale.order",
            "active_ids": [cls.sale_1.id],
            "active_id": cls.sale_1.id,
            "default_journal_id": cls.company_data["default_journal_sale"].id,
        }
        wizard = (
            cls.env["sale.advance.payment.inv"]
            .with_context(**context)
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        wizard.create_invoices()
        cls.invoice_1 = cls.sale_1.invoice_ids[0]
        cls.invoice_1.action_post()
        cls.client_2 = cls.env["res.partner"].create({"name": "Client 2"})
        cls.sale_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.client_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.productB.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.sale_2.action_confirm()
        cls.picking_2 = cls.sale_2.picking_ids[0]
        cls.batch = cls.env["stock.picking.batch"].create(
            {
                "name": "Batch 1",
                "company_id": cls.env.company.id,
            }
        )
        cls.type_operation = cls.picking_1.picking_type_id
        cls.type_document = [
            "pickings",
            "invoices",
            "invoices_and_pickings",
            "invoices_or_pickings",
        ]

    def test_stock_picking_batch_print_invoices_01(self):
        """Batch without pickings, with any configuration in operation type,
        batch mustn't print."""

        for (
            print_documents_from_batch,
            number_copies_pickings,
            number_copies_invoices,
        ) in itertools.product(self.type_document, *map(range, itertools.repeat(2, 2))):
            self.type_operation.update(
                {
                    "print_documents_from_batch": print_documents_from_batch,
                    "number_copies_pickings": number_copies_pickings,
                    "number_copies_invoices": number_copies_invoices,
                }
            )
            with self.assertRaises(UserError):
                self.batch.action_print_pickings()

    def test_stock_picking_batch_print_pickings_02(self):
        """Batch with pickings"""
        self.batch.update(
            {"picking_ids": [(6, 0, (self.picking_1 | self.picking_2).ids)]}
        )
        for (
            print_documents_from_batch,
            number_copies_pickings,
            number_copies_invoices,
        ) in itertools.product(self.type_document, *map(range, itertools.repeat(2, 2))):
            self.type_operation.update(
                {
                    "print_documents_from_batch": print_documents_from_batch,
                    "number_copies_pickings": number_copies_pickings,
                    "number_copies_invoices": number_copies_invoices,
                }
            )
            if (
                not number_copies_pickings
                and not number_copies_invoices
                or print_documents_from_batch == "pickings"
                and number_copies_pickings == 0
                or print_documents_from_batch == "invoice"
                and number_copies_invoices == 0
            ):
                # Check cases where the number of copies is 0 then prints nothing
                with self.assertRaises(UserError):
                    self.batch.action_print_pickings()
            elif (
                print_documents_from_batch
                in {"pickings", "invoices_and_pickings", "invoices_or_pickings"}
                and number_copies_pickings == 1
                and not number_copies_invoices
            ):
                # Check cases where print pickings and not print invoices
                self.type_operation.number_copies_pickings = 2
                self.check_print_document(self.batch, "pickings")
            elif (
                print_documents_from_batch
                in {"invoices", "invoices_and_pickings", "invoices_or_pickings"}
                and number_copies_invoices == 1
                and not number_copies_pickings
            ):
                # Check cases where print invoices and not print pickings
                self.type_operation.number_copies_invoices = 2
                self.check_print_document(self.batch, "invoices")
            else:
                self.type_operation.number_copies_pickings = 2
                self.type_operation.number_copies_invoices = 2
                if print_documents_from_batch == "pickings":
                    self.check_print_document(self.batch, "pickings")
                elif print_documents_from_batch == "invoices":
                    self.check_print_document(self.batch, "invoices")
                elif print_documents_from_batch == "invoices_and_pickings":
                    self.check_print_document(self.batch, "both")
                else:
                    self.check_print_document(self.batch, "no_both")

    def check_print_document(self, batch, type_document):
        result = batch.action_print_pickings()
        if (
            result.get("xml_id", False)
            and result["xml_id"] == "web.action_base_document_layout_configurator"
        ):
            result = result.get("context", {}).get("report_action", {})
        self.assertEqual(result.get("type"), "ir.actions.report")
        report_name = result.get("report_name")
        self.assertEqual(
            result.get("report_name"),
            "stock_picking_batch_print_pickings." "report_picking_batch_print_pickings",
        )
        report_pdf = self.env["ir.actions.report"]._render(report_name, self.batch.ids)
        self.assertGreaterEqual(len(report_pdf[0]), 1)
        if type_document == "pickings":
            self.assertEqual(str(report_pdf[0]).count(self.picking_1.name), 2)
            self.assertEqual(str(report_pdf[0]).count(self.picking_2.name), 2)
        elif type_document == "invoices":
            self.assertEqual(str(report_pdf[0]).count(self.invoice_1.name), 4)
        elif type_document == "both":
            self.assertEqual(str(report_pdf[0]).count(self.picking_1.name), 2)
            self.assertEqual(str(report_pdf[0]).count(self.picking_2.name), 2)
            self.assertEqual(str(report_pdf[0]).count(self.invoice_1.name), 4)
        else:
            self.assertEqual(str(report_pdf[0]).count(self.picking_2.name), 2)
            self.assertEqual(str(report_pdf[0]).count(self.invoice_1.name), 4)
