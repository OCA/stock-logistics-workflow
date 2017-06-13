# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.stock.tests.common import TestStockCommon


class TestStockPickingInvoiceLink(TestStockCommon):
    def setUp(self):
        super(TestStockPickingInvoiceLink, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.picking_in = self.PickingObj.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_in,
            'invoice_state': '2binvoiced'})
        self.MoveObj.create({
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 1,
            'product_uom': self.productA.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced',
        })
        self.MoveObj.create({
            'name': self.productB.name,
            'product_id': self.productB.id,
            'product_uom_qty': 1,
            'product_uom': self.productB.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced',
        })
        self.MoveObj.create({
            'name': self.productC.name,
            'product_id': self.productC.id,
            'product_uom_qty': 10,
            'product_uom': self.productC.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced',
        })
        self.MoveObj.create({
            'name': self.productD.name,
            'product_id': self.productD.id,
            'product_uom_qty': 10,
            'product_uom': self.productD.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced',
        })
        self.MoveObj.create({
            'name': self.productD.name,
            'product_id': self.productD.id,
            'product_uom_qty': 5,
            'product_uom': self.productD.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
        context = {"active_model": 'stock.picking',
                   "active_ids": [self.picking_in.id],
                   "active_id": self.picking_in.id}
        self.wizard = self.env['stock.invoice.onshipping'].with_context(
            context).create({})

    def test_invoice_create(self):
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')
        for move in self.picking_in.move_lines:
            self.assertEqual(move.invoice_state, '2binvoiced')
        self.wizard.open_invoice()
        self.assertTrue(self.picking_in.invoice_ids)
        invoice = self.picking_in.invoice_id
        self.assertTrue(invoice)
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        for move in self.picking_in.move_lines:
            self.assertTrue(move.invoice_line_ids)
            self.assertTrue(move.invoice_line_id)
            self.assertEqual(move.invoice_state, 'invoiced')
        invoice.action_cancel()
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')
        invoice.action_cancel_draft()
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        self.assertEqual(
            set(invoice.invoice_line.ids),
            set(self.picking_in.move_lines.mapped('invoice_line_id').ids))
        self.assertEqual(
            set(self.picking_in.move_lines.ids),
            set(invoice.invoice_line.mapped('move_line_ids').ids))

    def test_invoice_unlink_draft(self):
        self.wizard.open_invoice()
        self.picking_in.invoice_ids.unlink()
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')

    def test_invoice_unlink_cancel(self):
        self.wizard.open_invoice()
        self.picking_in.invoice_ids.signal_workflow('invoice_cancel')
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')

    def test_invoice_unlink_not_draft_nor_cancel(self):
        self.wizard.open_invoice()
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')

    def test_action_view_invoice(self):
        self.wizard.open_invoice()
        result = self.picking_in.action_view_invoice()
        self.assertEqual(result['views'][0][1], 'form')
        invoice = self.picking_in.invoice_ids
        self.assertEqual(result['res_id'], invoice.id)
