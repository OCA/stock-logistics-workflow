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
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create and post invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        # Only one invoice line has been created
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        line = invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped("move_line_ids")), 1)
        self.assertEqual(line.mapped("move_line_ids"), picking.move_lines)
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, invoice)

    def test_link_transfer_after_invoice_creation(self):
        self.product.purchase_method = "purchase"
        # Purchase order confirm
        self.po.button_confirm()
        # create and post invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
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

    def test_invoice_refund_invoice(self):
        """Check that the invoice created after a refund is linked to the stock
        picking.
        """
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"refund_method": "cancel", "reason": "test"})
        )
        wiz_invoice_refund.reverse_moves()
        # Create invoice again
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        new_inv = inv_form.save()
        # Assert that new invoice has related picking
        self.assertEqual(new_inv.picking_ids, picking)

    def test_invoice_refund_modify(self):
        """Check that the invoice created when the option "Full refund and new draft
        invoice" is selected, is linked to the picking.
        """
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"refund_method": "modify", "reason": "test"})
        )
        invoice_id = wiz_invoice_refund.reverse_moves()["res_id"]
        new_inv = self.env["account.move"].browse(invoice_id)
        self.assertEqual(new_inv.picking_ids, picking)
        self.assertTrue(len(picking.invoice_ids) == 3)

    def test_purchase_invoice_backorder_no_linked_policy_receive(self):
        self.product.purchase_method = "receive"
        self.po.order_line.product_qty = 10
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_lines.quantity_done = 8.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        self.assertTrue(len(picking.invoice_ids) == 1)
        self.assertEqual(invoice.picking_ids, picking)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_lines.quantity_done = 2.0
        backorder_picking.button_validate()
        self.assertFalse(len(backorder_picking.invoice_ids))
        self.assertEqual(invoice.picking_ids, picking)

    def test_purchase_invoice_backorder_linked_policy_purchase(self):
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 10
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_lines.quantity_done = 8.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        self.assertTrue(len(picking.invoice_ids) == 1)
        self.assertEqual(invoice.picking_ids, picking)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_lines.quantity_done = 2.0
        backorder_picking.button_validate()
        self.assertFalse(len(backorder_picking.invoice_ids) == 1)
        self.assertEqual(invoice.picking_ids, picking + backorder_picking)

    def test_partial_invoice_full_link(self):
        """Check that the partial invoices are linked to the stock
        picking.
        """
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 2.0
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_lines.quantity_done = 2.0
        picking.action_done()
        # Create invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        for i in range(len(inv_form.invoice_line_ids)):
            with inv_form.invoice_line_ids.edit(i) as line_form:
                line_form.quantity = 1
        inv = inv_form.save()
        inv.action_post()
        self.assertEqual(inv.picking_ids, picking)
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        inv2 = inv_form.save()
        self.assertEqual(inv2.picking_ids, picking)
