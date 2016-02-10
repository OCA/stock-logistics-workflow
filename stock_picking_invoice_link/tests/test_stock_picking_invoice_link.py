# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.stock.tests.common import TestStockCommon
from openerp import exceptions


class TestStockPickingInvoiceLink(TestStockCommon):
    def setUp(self):
        super(TestStockPickingInvoiceLink, self).setUp()
        self.picking_in = self.PickingObj.create({
            'partner_id': self.partner_delta_id,
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
            'invoice_state': '2binvoiced'})
        self.MoveObj.create({
            'name': self.productB.name,
            'product_id': self.productB.id,
            'product_uom_qty': 1,
            'product_uom': self.productB.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
        self.MoveObj.create({
            'name': self.productC.name,
            'product_id': self.productC.id,
            'product_uom_qty': 10,
            'product_uom': self.productC.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
        self.MoveObj.create({
            'name': self.productD.name,
            'product_id': self.productD.id,
            'product_uom_qty': 10,
            'product_uom': self.productD.uom_id.id,
            'picking_id': self.picking_in.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location,
            'invoice_state': '2binvoiced'})
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
        self.assertTrue(self.picking_in.invoice_id)
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        for move in self.picking_in.move_lines:
            self.assertTrue(move.invoice_line_id)
            self.assertEqual(move.invoice_state, 'invoiced')
        self.picking_in.invoice_id.action_cancel()
        self.assertEqual(self.picking_in.invoice_id.state, 'cancel')
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')
        self.picking_in.invoice_id.action_cancel_draft()
        self.assertEqual(self.picking_in.invoice_id.state, 'draft')
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')

    def test_invoice_unlink_draft(self):
        self.wizard.open_invoice()
        self.assertTrue(self.picking_in.invoice_id)
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        self.assertEqual(self.picking_in.invoice_id.state, 'draft')
        self.picking_in.invoice_id.unlink()
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')

    def test_invoice_unlink_cancel(self):
        self.wizard.open_invoice()
        self.assertTrue(self.picking_in.invoice_id)
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        self.picking_in.invoice_id.signal_workflow('invoice_cancel')
        self.assertEqual(self.picking_in.invoice_id.state, 'cancel')
        self.assertEqual(self.picking_in.invoice_state, '2binvoiced')
        self.picking_in.invoice_id.unlink()

    def test_invoice_unlink_not_draft_nor_cancel(self):
        self.wizard.open_invoice()
        self.assertTrue(self.picking_in.invoice_id)
        self.assertEqual(self.picking_in.invoice_state, 'invoiced')
        self.picking_in.invoice_id.signal_workflow('invoice_open')
        self.assertNotIn(self.picking_in.invoice_id.state, ['draft', 'cancel'])
        with self.assertRaises(exceptions.Warning):
            self.picking_in.invoice_id.unlink()

    def test_xml_id(self):
        picking_out = self.picking_in.copy(
            default={'picking_type_id': self.picking_type_out})
        for move in picking_out:
            move.write({'invoice_state': '2binvoiced'})
        context = {"active_model": 'stock.picking',
                   "active_ids": [picking_out.id],
                   "active_id": picking_out.id}
        wizard_out = self.env['stock.invoice.onshipping'].with_context(
            context).create({})
        self.wizard.open_invoice()
        wizard_out.open_invoice()
        self.assertEqual(self.picking_in.invoice_view_xmlid,
                         'account.invoice_supplier_form')
        self.assertEqual(picking_out.invoice_view_xmlid,
                         'account.invoice_form')
