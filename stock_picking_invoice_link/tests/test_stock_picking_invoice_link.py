# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale.tests.test_sale_common import TestSale


class TestStockPickingInvoiceLink(TestSale):
    def test_00_sale_stock_invoice_link(self):
        inv_obj = self.env['account.invoice']
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': p.name, 'product_id': p.id, 'product_uom_qty': 2,
                'product_uom': p.uom_id.id, 'price_unit': p.list_price
            }) for (_, p) in self.products.iteritems()],
            'pricelist_id': self.env.ref('product.list0').id,
            'picking_policy': 'direct',
        })
        self.so.action_confirm()
        self.assertTrue(self.so.picking_ids,
                        'Sale Stock: no picking created for '
                        '"invoice on delivery" stockable products')

        # invoice on order
        self.so.action_invoice_create()

        # deliver partially
        self.assertEqual(self.so.invoice_status, 'no',
                         'Sale Stock: so invoice_status should be '
                         '"nothing to invoice" after invoicing')
        pick_1 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing' and
            x.state in ('confirmed', 'partially_available'))
        pick_1.force_assign()
        pick_1.pack_operation_product_ids.write({'qty_done': 1})
        wiz_act = pick_1.do_new_transfer()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.process()
        self.assertEqual(self.so.invoice_status, 'to invoice',
                         'Sale Stock: so invoice_status should be '
                         '"to invoice" after partial delivery')
        inv_id = self.so.action_invoice_create()
        inv_1 = inv_obj.browse(inv_id)

        # complete the delivery
        self.assertEqual(self.so.invoice_status, 'no',
                         'Sale Stock: so invoice_status should be '
                         '"nothing to invoice" after partial delivery '
                         'and invoicing')
        self.assertEqual(len(self.so.picking_ids), 2,
                         'Sale Stock: number of pickings should be 2')
        pick_2 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing' and
            x.state in ('confirmed', 'partially_available'))
        pick_2.force_assign()
        pick_2.pack_operation_product_ids.write({'qty_done': 1})
        self.assertIsNone(pick_2.do_new_transfer(),
                          'Sale Stock: second picking should be '
                          'final without need for a backorder')
        self.assertEqual(self.so.invoice_status, 'to invoice',
                         'Sale Stock: so invoice_status should be '
                         '"to invoice" after complete delivery')
        inv_id = self.so.action_invoice_create()
        inv_2 = inv_obj.browse(inv_id)
        self.assertEqual(self.so.invoice_status, 'invoiced',
                         'Sale Stock: so invoice_status should be '
                         '"fully invoiced" after complete delivery and '
                         'invoicing')

        # Check links
        self.assertEqual(
            inv_1.picking_ids, pick_1,
            "Invoice 1 must link to only First Partial Delivery")
        self.assertEqual(
            inv_1.invoice_line_ids.mapped('move_line_ids'),
            pick_1.move_lines.filtered(
                lambda x: x.product_id.invoice_policy == "delivery"),
            "Invoice 1 lines must link to only First Partial Delivery lines")
        self.assertEqual(
            inv_2.picking_ids, pick_2,
            "Invoice 2 must link to only Second Delivery")
        self.assertEqual(
            inv_2.invoice_line_ids.mapped('move_line_ids'),
            pick_2.move_lines.filtered(
                lambda x: x.product_id.invoice_policy == "delivery"),
            "Invoice 2 lines must link to only Second Delivery lines")
