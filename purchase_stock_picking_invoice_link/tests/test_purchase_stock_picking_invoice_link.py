# Copyright 2019 Vicent Cubells <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields
from odoo.tests import Form, common, tagged


@tagged("-at_install", "post_install")
class TestPurchaseSTockPickingInvoiceLink(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
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
        picking.move_line_ids.qty_done = 1.0
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
        picking.move_line_ids.qty_done = 1.0
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
        picking.move_line_ids.qty_done = 1.0
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
                    "refund_method": "cancel",
                    "reason": "test",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        wiz_invoice_refund.reverse_moves()
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
        picking.move_line_ids.qty_done = 1.0
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
                    "refund_method": "modify",
                    "reason": "test",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        invoice_id = wiz_invoice_refund.reverse_moves()["res_id"]
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
        picking.move_line_ids.qty_done = 8.0
        picking._action_done()
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(invoice.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 1)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_line_ids.qty_done = 2.0
        backorder_picking.button_validate()
        self.assertFalse(len(backorder_picking.invoice_ids))
        self.assertEqual(invoice.picking_ids, picking)

    def test_purchase_invoice_backorder_linked_policy_purchase(self):
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 10
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.move_line_ids.qty_done = 8.0
        picking._action_done()
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        inv_action = self.po.action_create_invoice()
        invoice = self.env["account.move"].browse([(inv_action["res_id"])])
        self.assertEqual(invoice.picking_ids, picking)
        self.assertEqual(len(picking.invoice_ids), 1)
        backorder_picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        backorder_picking.move_line_ids.qty_done = 2.0
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
        picking.move_line_ids.qty_done = 2.0
        picking._action_done()
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

    def test_partial_invoice_separate_pickings(self):
        """Each partial invoice from a different picking links only to its
        corresponding picking moves.
        """
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 4.0
        self.po.button_confirm()
        po_line = self.po.order_line
        # First picking: partial 2 of 4, leaves a backorder
        picking_1 = self.po.picking_ids[0]
        picking_1.move_line_ids.qty_done = 2.0
        picking_1._action_done()
        self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking_1.id)]}
        ).process()
        # First invoice for the 2 received
        inv_action = self.po.action_create_invoice()
        invoice_1 = self.env["account.move"].browse(inv_action["res_id"])
        inv_form = Form(invoice_1)
        inv_form.invoice_date = fields.Date.today()
        with inv_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = 2
        invoice_1 = inv_form.save()
        invoice_1.action_post()
        # Second picking (backorder): 2 of 2
        picking_2 = self.po.picking_ids.filtered(lambda p: p.state != "done")
        picking_2.move_line_ids.qty_done = 2.0
        picking_2.button_validate()
        # Second invoice for the remaining 2
        inv_action = self.po.action_create_invoice()
        invoice_2 = self.env["account.move"].browse(inv_action["res_id"])
        invoice_2.invoice_date = fields.Date.today()
        invoice_2.action_post()
        # Each invoice must link only to its corresponding picking. Filter
        # by purchase_line_id so downstream modules adding ancillary lines
        # (e.g. purchase_invoice_new_picking_line) do not break the asserts.
        inv1_line = invoice_1.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        inv2_line = invoice_2.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        self.assertEqual(invoice_1.picking_ids, picking_1)
        self.assertEqual(invoice_2.picking_ids, picking_2)
        self.assertEqual(inv1_line.move_line_ids, picking_1.move_ids)
        self.assertEqual(inv2_line.move_line_ids, picking_2.move_ids)

    def test_claimed_skips_cancelled_invoice_lines(self):
        """Coverage: invoice lines whose parent move is cancelled must not
        count toward the move's claimed qty, so the move is re-linkable
        on the next invoice.
        """
        self.po.button_confirm()
        po_line = self.po.order_line
        picking = self.po.picking_ids[0]
        move = picking.move_ids
        picking.move_line_ids.qty_done = 1.0
        picking.button_validate()
        inv1 = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        inv1.invoice_date = fields.Date.today()
        inv1.action_post()
        inv1.button_cancel()
        inv2 = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        # The only invoice line tied to the move is the cancelled one;
        # claimed should be 0 and the move should be re-linked to inv2.
        inv2_line = inv2.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        self.assertEqual(inv2_line.move_line_ids, move)

    def test_claimed_subtracts_credit_notes(self):
        """Coverage: a credit note linked to the same move subtracts from
        the claimed qty, so a fully-refunded move is treated as
        unclaimed again on the next invoice.
        """
        self.po.button_confirm()
        # Capture the PO line and stock.move before validation so we keep
        # singleton references even if other modules (e.g.
        # purchase_invoice_new_picking_line) add extra order lines later.
        po_line = self.po.order_line
        picking = self.po.picking_ids[0]
        move = picking.move_ids
        picking.move_line_ids.qty_done = 1.0
        picking.button_validate()
        inv1 = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        inv1.invoice_date = fields.Date.today()
        inv1.action_post()
        # Manually create a credit note that points to the same PO line
        # and the same stock.move so the in_refund branch of the
        # claimed computation fires.
        refund = self.env["account.move"].create(
            {
                "move_type": "in_refund",
                "partner_id": self.supplier.id,
                "journal_id": inv1.journal_id.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1.0,
                            "price_unit": 15.0,
                            "purchase_line_id": po_line.id,
                            "move_line_ids": [(6, 0, move.ids)],
                        },
                    )
                ],
            }
        )
        refund.action_post()
        # qty_invoiced is now 0 net (inv1 +1, refund -1) so the next
        # invoice will be re-created and must include the move via the
        # in_refund subtraction path.
        inv2 = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        inv2_line = inv2.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        self.assertEqual(inv2_line.move_line_ids, move)

    def test_sequential_drafts_to_refund_moves(self):
        """Reproduce a scenario where receipt moves are flagged
        to_refund=True (e.g. by a connector). With several pickings of the
        same PO line invoiced as separate drafts before any is posted,
        each draft must only link to its own picking moves: the sign flip
        in get_stock_moves_link_invoice's to_invoice computation for
        to_refund moves used to pull every previously linked move into the
        new draft.
        """
        self.product.purchase_method = "receive"
        self.po.order_line.product_qty = 12.0
        self.po.button_confirm()
        po_line = self.po.order_line
        pickings = []
        invoices = []
        for qty in (3.0, 2.0, 5.0, 2.0):
            picking = self.po.picking_ids.filtered(lambda p: p.state != "done")[:1]
            picking.move_line_ids.qty_done = qty
            picking.move_ids.to_refund = True
            picking._action_done()
            if self.po.picking_ids.filtered(lambda p: p.state != "done"):
                self.env["stock.backorder.confirmation"].create(
                    {"pick_ids": [(4, picking.id)]}
                ).process()
            pickings.append(picking)
            inv_action = self.po.action_create_invoice()
            invoice = self.env["account.move"].browse(inv_action["res_id"])
            invoice.invoice_date = fields.Date.today()
            invoices.append(invoice)
        for picking, invoice in zip(pickings, invoices):
            inv_line = invoice.invoice_line_ids.filtered(
                lambda line: line.purchase_line_id == po_line
            )
            self.assertEqual(
                inv_line.move_line_ids,
                picking.move_ids,
                f"Draft {invoice.id} should only link to picking {picking.id} "
                f"moves, got {inv_line.move_line_ids.ids}",
            )

    def test_write_skips_cancelled_invoice_in_search(self):
        """When a posted invoice is cancelled before a backorder is
        validated, ``write()`` on the backorder move must not pick the
        cancelled invoice's line as candidate. The line's ``quantity``
        is still uncovered by its ``move_line_ids`` so without the
        ``move_id.state`` domain filter the new move would be linked to
        an abandoned draft.
        """
        self.product.purchase_method = "purchase"
        self.po.order_line.product_qty = 4.0
        self.po.button_confirm()
        po_line = self.po.order_line
        picking_1 = self.po.picking_ids[0]
        picking_1.move_line_ids.qty_done = 2.0
        picking_1._action_done()
        self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking_1.id)]}
        ).process()
        inv1 = self.env["account.move"].browse(
            self.po.action_create_invoice()["res_id"]
        )
        inv_form = Form(inv1)
        inv_form.invoice_date = fields.Date.today()
        with inv_form.invoice_line_ids.edit(0) as line_form:
            line_form.quantity = 2
        inv1 = inv_form.save()
        inv1.action_post()
        inv1.button_cancel()
        # Validate the backorder after inv1 is cancelled. write() must
        # exclude inv1's line via the move_id.state domain filter.
        picking_2 = self.po.picking_ids.filtered(lambda p: p.state != "done")
        picking_2.move_line_ids.qty_done = 2.0
        picking_2.button_validate()
        inv1_line = inv1.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        self.assertEqual(inv1_line.move_line_ids, picking_1.move_ids)

    def test_write_handles_alternative_uom(self):
        """Backorder linked to a single invoice when the PO line uses a
        UoM different from the product reference UoM (e.g. dozens for a
        product measured in units). The cobertura check in write() must
        normalise via ``_compute_quantity`` so the cumulated qty is
        compared in the invoice line UoM. Without conversion the filter
        would mix magnitudes and either miss or duplicate the link.
        """
        uom_dozen = self.env.ref("uom.product_uom_dozen")
        self.product.purchase_method = "purchase"
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 2.0,
                            "product_uom": uom_dozen.id,
                            "price_unit": 15.0,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        po.button_confirm()
        po_line = po.order_line
        # Note: _prepare_stock_moves pivots the move to the product
        # reference UoM (Unit) so qty_done is set in units: 12 = 1 dozen.
        picking_1 = po.picking_ids[0]
        picking_1.move_line_ids.qty_done = 12.0
        picking_1._action_done()
        self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking_1.id)]}
        ).process()
        # Invoice for the full ordered qty (2 dozens) covers both
        # pickings; the backorder's write() must extend the link via
        # the cobertura comparison after _compute_quantity conversion
        # of move qty (units) into invoice line UoM (dozens).
        inv = self.env["account.move"].browse(po.action_create_invoice()["res_id"])
        inv.invoice_date = fields.Date.today()
        inv.action_post()
        picking_2 = po.picking_ids.filtered(lambda p: p.state != "done")
        picking_2.move_line_ids.qty_done = 12.0
        picking_2.button_validate()
        inv_line = inv.invoice_line_ids.filtered(
            lambda line: line.purchase_line_id == po_line
        )
        self.assertEqual(
            inv_line.move_line_ids, picking_1.move_ids | picking_2.move_ids
        )
