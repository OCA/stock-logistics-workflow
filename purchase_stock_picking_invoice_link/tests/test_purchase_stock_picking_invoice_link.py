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
        backorder_wizard = Form(
            self.env["stock.backorder.confirmation"].with_context(
                **action_data["context"]
            )
        ).save()
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
        backorder_wizard = Form(
            self.env["stock.backorder.confirmation"].with_context(
                **action_data["context"]
            )
        ).save()
        backorder_wizard.process()
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(invoice.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 1)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_line_ids.quantity = 2.0
        backorder_picking.button_validate()
        self.assertEqual(invoice.picking_ids, picking + backorder_picking)

    def test_invoice_link_candidate_predicate(self):
        """Verify ``_is_purchase_invoice_link_candidate`` accepts supplier,
        transit, and subcontracting endpoints, and rejects unrelated
        locations. Subcontracting cases are skipped if
        ``mrp_subcontracting`` is not installed.
        """
        Location = self.env["stock.location"]
        StockMove = self.env["stock.move"]
        supplier_loc = Location.search([("usage", "=", "supplier")], limit=1)
        internal_loc = Location.search([("usage", "=", "internal")], limit=1)
        transit_loc = Location.create(
            {
                "name": "Test Transit Location",
                "usage": "transit",
                "company_id": False,
            }
        )
        other_internal = Location.create(
            {
                "name": "Other Internal",
                "usage": "internal",
                "company_id": self.env.company.id,
            }
        )
        common_vals = {
            "name": "Test move",
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
            "state": "done",
        }
        # Forward: supplier -> internal (existing behaviour)
        move_from_supplier = StockMove.new(
            {
                **common_vals,
                "location_id": supplier_loc.id,
                "location_dest_id": internal_loc.id,
            }
        )
        self.assertTrue(move_from_supplier._is_purchase_invoice_link_candidate())
        # Forward: transit -> internal (intercompany; the fix)
        move_from_transit = StockMove.new(
            {
                **common_vals,
                "location_id": transit_loc.id,
                "location_dest_id": internal_loc.id,
            }
        )
        self.assertTrue(move_from_transit._is_purchase_invoice_link_candidate())
        # Internal-only: must be rejected
        move_internal = StockMove.new(
            {
                **common_vals,
                "location_id": internal_loc.id,
                "location_dest_id": other_internal.id,
            }
        )
        self.assertFalse(move_internal._is_purchase_invoice_link_candidate())
        # Return: internal -> supplier with to_refund (existing behaviour)
        move_return = StockMove.new(
            {
                **common_vals,
                "location_id": internal_loc.id,
                "location_dest_id": supplier_loc.id,
                "to_refund": True,
            }
        )
        self.assertTrue(move_return._is_purchase_invoice_link_candidate())
        # Return to transit with to_refund (the fix, return path)
        move_return_transit = StockMove.new(
            {
                **common_vals,
                "location_id": internal_loc.id,
                "location_dest_id": transit_loc.id,
                "to_refund": True,
            }
        )
        self.assertTrue(move_return_transit._is_purchase_invoice_link_candidate())
        # Return to supplier WITHOUT to_refund: must be rejected
        move_return_no_refund = StockMove.new(
            {
                **common_vals,
                "location_id": internal_loc.id,
                "location_dest_id": supplier_loc.id,
            }
        )
        self.assertFalse(move_return_no_refund._is_purchase_invoice_link_candidate())
        # Scrapped move: must be rejected even if endpoints match
        move_scrapped = StockMove.new(
            {
                **common_vals,
                "location_id": supplier_loc.id,
                "location_dest_id": internal_loc.id,
                "scrapped": True,
            }
        )
        self.assertFalse(move_scrapped._is_purchase_invoice_link_candidate())
        # Non-done move: must be rejected
        move_draft = StockMove.new(
            {
                **common_vals,
                "location_id": supplier_loc.id,
                "location_dest_id": internal_loc.id,
                "state": "draft",
            }
        )
        self.assertFalse(move_draft._is_purchase_invoice_link_candidate())
        # Subcontracting receipt: source location flagged as subcontract
        # (skip when mrp_subcontracting is not installed)
        if "is_subcontracting_location" not in Location._fields:
            return
        subcontract_loc = Location.create(
            {
                "name": "Test Subcontract Location",
                "usage": "internal",
                "is_subcontracting_location": True,
                "company_id": self.env.company.id,
            }
        )
        move_from_subcontract = StockMove.new(
            {
                **common_vals,
                "location_id": subcontract_loc.id,
                "location_dest_id": internal_loc.id,
            }
        )
        self.assertTrue(move_from_subcontract._is_purchase_invoice_link_candidate())
        # Return to subcontract location with to_refund
        move_return_subcontract = StockMove.new(
            {
                **common_vals,
                "location_id": internal_loc.id,
                "location_dest_id": subcontract_loc.id,
                "to_refund": True,
            }
        )
        self.assertTrue(move_return_subcontract._is_purchase_invoice_link_candidate())

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
        inv_form = Form(invoice)
        inv_form.invoice_date = fields.Date.today()
        for i in range(len(inv_form.invoice_line_ids)):
            with inv_form.invoice_line_ids.edit(i) as line_form:
                line_form.quantity = 1
        inv = inv_form.save()
        inv.action_post()
        self.assertEqual(inv.picking_ids, picking)
        inv_action = self.po.action_create_invoice()
        inv2 = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(inv2.picking_ids, picking)
