# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2021 Tecnativa - João Marques
# Copyright 2025 Akretion - Renato Lima <renato.lima@akretion.com.br>
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestStockPickingInvoiceLink(AccountTestInvoicingCommon):
    @classmethod
    def _create_stock_picking_and_confirm(cls):
        picking_form = Form(
            cls.env["stock.picking"].with_context(
                default_picking_type_id=cls.picking_type_out.id,
                default_partner_id=cls.partner_a.id,
            )
        )
        for product in cls.product_a + cls.product_b + cls.product_c:
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 2
        picking = picking_form.save()
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
                "partner_id": cls.partner_a.id,
            }
        )
        for move in picking.move_ids:
            cls.env["account.move.line"].create(
                {
                    "move_id": invoice.id,
                    "move_line_ids": [Command.set(move.ids)],
                    "name": move.name,
                    "quantity": move.product_uom_qty,
                    "price_unit": move.price_unit,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "tax_ids": [Command.set(move.product_id.taxes_id.ids)],
                }
            )
        picking.write({"invoice_ids": [Command.set(invoice.ids)]})
        invoice.action_post()
        return invoice

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a.is_storable = True
        cls.product_b.is_storable = True
        cls.product_c = cls._create_product(
            name="product_c",
            type="consu",
            is_storable=True,
        )
        # Stock Location
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company_data["company"].id)], limit=1
        )
        cls.location = warehouse.lot_stock_id
        cls.picking_type_out = warehouse.out_type_id
        # Update product quantities
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_a, cls.location, 100.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_b, cls.location, 100.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_c, cls.location, 100.0
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

    @mute_logger("odoo.models.unlink")
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
        for return_line in return_wiz.product_return_moves:
            return_line.to_refund = True
            return_line.quantity = return_line.move_quantity
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
