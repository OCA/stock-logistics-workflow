# Copyright 2019 Vicent Cubells <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields
from odoo.tests import common


class TestPurchaseSTockPickingInvoiceLink(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseSTockPickingInvoiceLink, cls).setUpClass()

        cls.supplier = cls.env["res.partner"].create({"name": "Supplier for Test"})
        product = cls.env["product.product"].create({"name": "Product for Test"})
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "product_qty": 1.0,
                            "date_planned": fields.date.today(),
                            "product_uom": product.uom_po_id.id,
                            "price_unit": 15.0,
                        },
                    )
                ],
            }
        )

    def test_puchase_stock_picking_invoice_link(self):
        # Purchase order confirm
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        self.invoice = self.env["account.move"].create(
            {
                "partner_id": self.supplier.id,
                "purchase_id": self.po.id,
                "company_id": self.po.company_id.id,
                "type": "in_invoice",
                "invoice_origin": self.po.name,
                "ref": self.po.partner_ref,
            }
        )
        self.invoice._onchange_purchase_auto_complete()
        self.invoice.action_post()
        # Only one invoice line has been created
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        line = self.invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped("move_line_ids")), 1)
        self.assertEqual(line.mapped("move_line_ids"), picking.move_lines)
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, self.invoice)
