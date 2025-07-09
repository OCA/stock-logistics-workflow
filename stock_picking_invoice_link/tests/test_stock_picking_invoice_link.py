# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2021 Tecnativa - João Marques
# Copyright 2025 Akretion - Renato Lima <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.stock.tests.common import TestStockCommon


@tagged("post_install", "-at_install")
class TestStockPickingInvoiceLink(TestStockCommon):
    @classmethod
    def _create_stock_picking_and_confirm(cls):
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partnerA.id,
                "location_id": cls.stock_location,
                "location_dest_id": cls.customer_location,
                "picking_type_id": cls.picking_type_out,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.productA.name,
                            "product_id": cls.productA.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.productA.uom_id.id,
                            "price_unit": cls.productA.list_price,
                            "location_id": cls.stock_location,
                            "location_dest_id": cls.customer_location,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.productB.name,
                            "product_id": cls.productB.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.productB.uom_id.id,
                            "price_unit": cls.productB.list_price,
                            "location_id": cls.stock_location,
                            "location_dest_id": cls.customer_location,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.productC.name,
                            "product_id": cls.productC.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.productC.uom_id.id,
                            "price_unit": cls.productC.list_price,
                            "location_id": cls.stock_location,
                            "location_dest_id": cls.customer_location,
                        },
                    ),
                ],
            }
        )
        picking.action_assign()
        picking.move_line_ids.write({"quantity": 2})
        picking.button_validate()
        return picking

    @classmethod
    def _create_account_invoice_and_confirm(cls, picking):
        invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_date": "2017-01-01",
                "date": "2017-01-01",
                "partner_id": cls.partnerA.id,
                "currency_id": cls.env.company.currency_id.id,
            }
        )

        for move in picking.move_ids:
            cls.env["account.move.line"].create(
                {
                    "move_id": invoice.id,
                    "move_line_ids": [(6, 0, move.ids)],
                    "name": move.name,
                    "quantity": move.product_uom_qty,
                    "price_unit": move.price_unit,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "tax_ids": [(6, 0, move.product_id.taxes_id.ids)],
                }
            )

        picking.write({"invoice_ids": [(6, 0, invoice.ids)]})
        invoice.action_post()
        return invoice

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        # Create partner
        cls.partnerA = cls.PartnerObj.create({"name": "SuperPartner"})

        # Stock Location
        cls.location = cls.StockLocationObj.browse(cls.stock_location)

        # Update product quantities
        cls.env["stock.quant"]._update_available_quantity(
            cls.productA, cls.location, 100.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.productB, cls.location, 100.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.productC, cls.location, 100.0
        )

        # Create demo picking
        cls.pickingA = cls._create_stock_picking_and_confirm()
        # Create demo invoice
        cls.invoiceA = cls._create_account_invoice_and_confirm(cls.pickingA)

    def test_00_sale_stock_invoice_link(self):
        """Test the stock picking invoice relation"""
        self.assertEqual(
            self.pickingA.invoice_ids,
            self.invoiceA,
            "Stock Picking: Stock picking should be " "an invoice related ",
        )

    def test_01_sale_stock_invoice_link(self):
        """Test the stock picking invoice link button"""
        result = self.pickingA.action_view_invoice()
        self.assertEqual(result["views"][0][1], "form")
        self.assertEqual(result["res_id"], self.invoiceA.id)

    def test_02_sale_stock_invoice_link(self):
        """Test the stock picking and invoice return"""
        # Create return picking
        return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_id=self.pickingA.ids[0],
                active_model="stock.picking",
            )
        )
        return_wiz = return_form.save()
        # Remove product ordered line
        return_wiz.product_return_moves.to_refund = True
        res = return_wiz.action_create_returns()
        return_picking = self.env["stock.picking"].browse(res["res_id"])
        # Validate picking
        return_picking.move_line_ids.write({"quantity": 2})
        return_picking.button_validate()
        # Create Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoiceA.ids)
            .create(
                {
                    "reason": "test",
                    "journal_id": self.invoiceA.journal_id.id,
                }
            )
        )

        action = wiz_invoice_refund.refund_moves()
        invoice_refund = self.env["account.move"].browse(action["res_id"])

        self.assertEqual(
            return_picking,
            invoice_refund.picking_ids,
            "Stock Picking Return: Stock picking should be an invoice related ",
        )
