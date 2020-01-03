# Copyright 2019 Vicent Cubells <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from odoo import fields


class TestPurchaseSTockPickingInvoiceLink(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseSTockPickingInvoiceLink, cls).setUpClass()

        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier for Test',
            'supplier': True,
        })
        product = cls.env['product.product'].create({
            'name': 'Product for Test',
        })
        cls.po = cls.env['purchase.order'].create({
            'partner_id': cls.supplier.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_qty': 1.0,
                'date_planned': fields.date.today(),
                'product_uom': product.uom_po_id.id,
                'price_unit': 15.0,
            })]
        })

    def test_puchase_stock_picking_invoice_link(self):
        # Purchase order confirm
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Invoice purchase
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.supplier.id,
            'purchase_id': self.po.id,
            'account_id': self.supplier.property_account_payable_id.id,
            'type': 'in_invoice',
        })
        self.invoice.purchase_order_change()
        self.invoice.action_invoice_open()
        # Only one invoice line has been created
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        line = self.invoice.invoice_line_ids
        # Move lines are set in invoice lines
        self.assertEqual(len(line.mapped('move_line_ids')), 1)
        self.assertEqual(line.mapped('move_line_ids'), picking.move_lines)
        # Invoices are set in pickings
        self.assertEqual(picking.invoice_ids, self.invoice)
