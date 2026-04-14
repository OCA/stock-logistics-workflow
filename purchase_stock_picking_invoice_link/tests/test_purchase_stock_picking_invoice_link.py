# Copyright 2019 Vicent Cubells <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields
from odoo.tests import Form, common, tagged


@tagged("-at_install", "post_install")
class TestPurchaseSTockPickingInvoiceLink(common.TransactionCase):
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
        picking.move_line_ids.quantity = 1.0
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
        self.assertEqual(len(line.mapped("move_line_ids").mapped("move_line_ids")), 1)
        self.assertEqual(
            line.mapped("move_line_ids").mapped("move_line_ids"), picking.move_line_ids
        )
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, invoice)

    def test_link_transfer_after_invoice_creation(self):
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
        picking.move_line_ids.quantity = 1.0
        picking.button_validate()
        # Only one invoice line has been created
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        line = invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped("move_line_ids").mapped("move_line_ids")), 1)
        self.assertEqual(
            line.mapped("move_line_ids").mapped("move_line_ids"), picking.move_line_ids
        )
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
        picking.move_line_ids.quantity = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        invoice.invoice_date = self.po.create_date
        invoice.action_post()
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "reason": "test",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        wiz_invoice_refund.refund_moves()
        # Create invoice again
        inv_action = self.po.action_create_invoice()
        new_inv = self.env["account.move"].browse([(inv_action["res_id"])])
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
        picking.move_line_ids.quantity = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        invoice.invoice_date = self.po.create_date
        invoice.action_post()
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "reason": "test",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        invoice_id = wiz_invoice_refund.modify_moves()["res_id"]
        new_inv = self.env["account.move"].browse(invoice_id)
        # Maintain order due to a bug in the ORM that does not populate compute before
        # evaluating the len() function.
        # Bug reported on: https://github.com/odoo/odoo/issues/98981
        self.assertEqual(new_inv.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 3)

    def test_purchase_invoice_backorder_no_linked_policy_receive(self):
        self.product.purchase_method = "receive"
        self.po.order_line.product_qty = 10
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_line_ids.quantity = 8.0
        action_data = picking.button_validate()
        backorder_wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(**action_data["context"])
            .create({})
        )
        backorder_wizard.process()
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(invoice.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 1)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_line_ids.quantity = 2.0
        backorder_picking.button_validate()
        self.assertFalse(len(backorder_picking.invoice_ids))
        self.assertEqual(invoice.picking_ids, picking)

    def test_purchase_invoice_backorder_linked_policy_purchase(self):
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 10
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_line_ids.quantity = 8.0
        action_data = picking.button_validate()
        backorder_wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(**action_data["context"])
            .create({})
        )
        backorder_wizard.process()
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(invoice.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 1)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_line_ids.quantity = 2.0
        backorder_picking.button_validate()
        self.assertEqual(invoice.picking_ids, picking + backorder_picking)

    def test_partial_invoice_full_link(self):
        """Check that the partial invoices are linked to the stock
        picking.
        """
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 2.0
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_line_ids.quantity = 2.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        invoice.write({"invoice_date": fields.Date.today()})
        for line in invoice.invoice_line_ids:
            line.write({"quantity": 1})
        invoice.action_post()
        inv = invoice
        self.assertEqual(inv.picking_ids, picking)
        inv_action = self.po.action_create_invoice()
        inv2 = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(inv2.picking_ids, picking)

    def test_purchase_return_after_refund(self):
        self.product.purchase_method = "purchase"
        self.po.button_confirm()

        # 1. Create invoice BEFORE receiving products (purchase method="purchase")
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([inv_action["res_id"]])
        invoice.invoice_date = self.po.create_date
        invoice.action_post()

        # 2. Refund the invoice (Credit Note)
        wiz_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"reason": "test refund", "journal_id": invoice.journal_id.id})
        )
        wiz_refund.refund_moves()
        refund_invoice = self.env["account.move"].search(
            [("reversed_entry_id", "=", invoice.id)]
        )
        refund_invoice.action_post()

        # 3. Receive products (which should link to original invoice)
        picking = self.po.picking_ids[0]
        picking.move_line_ids.quantity = 1.0
        picking.button_validate()

        # 4. Return the products (should link to refund invoice)
        ctx = {"active_id": picking.id, "active_ids": picking.ids}
        fields = list(self.env["stock.return.picking"]._fields.keys())
        default_vals = (
            self.env["stock.return.picking"].with_context(**ctx).default_get(fields)
        )
        default_vals["picking_id"] = picking.id
        default_vals["product_return_moves"] = [
            (
                0,
                0,
                {
                    "product_id": m.product_id.id,
                    "quantity": m.quantity,
                    "move_id": m.id,
                    "uom_id": m.product_id.uom_id.id,
                },
            )
            for m in picking.move_ids
        ]
        return_wiz = (
            self.env["stock.return.picking"].with_context(**ctx).create(default_vals)
        )
        return_wiz_action = return_wiz.action_create_returns()
        return_picking = self.env["stock.picking"].browse(return_wiz_action["res_id"])

        # Validate the return
        return_picking.move_line_ids.quantity = 1.0
        return_picking.button_validate()

        refund_invoice._compute_picking_ids()
        self.assertEqual(return_picking.invoice_ids, refund_invoice)

    def test_over_invoiced_filtered(self):
        """Test that if qty_invoiced > product_qty, stock moves to_refund
        are filtered out, and test that zero to_invoice breaks out when
        invoice lines exist."""
        self.product.purchase_method = "purchase"
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_line_ids.quantity = 1.0
        picking.button_validate()

        # Invoice 1
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([inv_action["res_id"]])
        invoice.invoice_date = self.po.create_date
        invoice.action_post()

        # Link moves logic hit manually
        po_line = self.po.order_line[0]

        # 1) Force to_invoice = 0 by making product_qty = qty_invoiced (which is 1)
        # And ensure the stock move has invoice_line_ids (from above).
        # This should hit float_is_zero -> break logic
        moves = po_line.get_stock_moves_link_invoice()
        self.assertFalse(moves)

        # 2) Force qty_invoiced > product_qty
        # Since we cannot easily modify validated invoices to bump qty_invoiced,
        # we can decrease product_qty on the PO.
        po_line.write({"product_qty": 0.5})

        # Now product_qty (0.5) - qty_invoiced (1.0) < 0
        # Call _prepare_account_move_line to trigger to_refund evaluation
        vals = po_line._prepare_account_move_line(invoice)
        self.assertTrue("move_line_ids" in vals)
