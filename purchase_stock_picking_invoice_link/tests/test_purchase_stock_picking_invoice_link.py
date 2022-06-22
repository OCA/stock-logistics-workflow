# Copyright 2019 Vicent Cubells <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form, common


class TestPurchaseSTockPickingInvoiceLink(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier for Test"})
        cls.product = cls.env["product.product"].create({"name": "Product for Test"})
        po_form = Form(cls.env["purchase.order"])
        po_form.partner_id = cls.supplier
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = cls.product
            po_line_form.price_unit = 15.0
        cls.po = po_form.save()

    def test_puchase_stock_picking_invoice_link(self):
        # Purchase order confirm
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create and post invoice
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        invoice.invoice_date = self.po.create_date
        invoice._compute_picking_ids()
        invoice.action_post()
        # Only one invoice line has been created
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        line = invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped("move_line_ids")), 1)
        self.assertEqual(line.mapped("move_line_ids"), picking.move_lines)
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, invoice)

    def test_link_with_on_receive_quantities_policy(self):
        self.product.purchase_method = "purchase"
        # Purchase order confirm
        self.po.button_confirm()
        # create and post invoice
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        invoice.invoice_date = self.po.create_date
        invoice.action_post()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Only one invoice line has been created
        self.assertEqual(len(invoice.invoice_line_ids), 1)

        line = invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped("move_line_ids")), 1)
        self.assertEqual(line.mapped("move_line_ids"), picking.move_lines)
        self.assertEqual(len(invoice.picking_ids), 1)
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, invoice)
