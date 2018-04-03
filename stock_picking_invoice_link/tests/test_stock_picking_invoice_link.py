# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.sale.tests.test_sale_common import TestSale


class TestStockPickingInvoiceLink(TestSale):

    def _update_product_qty(self, product, location):
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': 100.0,
        })
        product_qty.change_product_qty()
        return product_qty

    def setUp(self):
        super(TestStockPickingInvoiceLink, self).setUp()
        company = self.env.ref('base.main_company')
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', company.id)], limit=1)
        stock_location = warehouse.lot_stock_id
        for (_, p) in self.products.items():
            if p.type == 'product':
                self._update_product_qty(p, stock_location)
        prod_order = self.products['prod_order']
        prod_del = self.products['prod_del']
        serv_order = self.products['serv_order']
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': prod_order.name, 'product_id': prod_order.id,
                    'product_uom_qty': 2, 'product_uom': prod_order.uom_id.id,
                    'price_unit': prod_order.list_price
                }),
                (0, 0, {
                    'name': prod_del.name, 'product_id': prod_del.id,
                    'product_uom_qty': 2, 'product_uom': prod_del.uom_id.id,
                    'price_unit': prod_del.list_price
                }),
                (0, 0, {
                    'name': serv_order.name, 'product_id': serv_order.id,
                    'product_uom_qty': 2, 'product_uom': serv_order.uom_id.id,
                    'price_unit': serv_order.list_price
                }),
            ],
            'pricelist_id': self.env.ref('product.list0').id,
            'picking_policy': 'direct',
        })
        self.so.action_confirm()

    def test_00_sale_stock_invoice_link(self):
        inv_obj = self.env['account.invoice']
        pick_obj = self.env['stock.picking']
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
            x.state in ('confirmed', 'assigned', 'partially_available'))
        pick_1.force_assign()
        pick_1.move_line_ids.write({'qty_done': 1})
        pick_1.action_done()
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
            x.state in ('confirmed', 'assigned', 'partially_available'))
        pick_2.force_assign()
        pick_2.move_line_ids.write({'qty_done': 1})
        pick_2.action_done()
        backorders = pick_obj.search([('backorder_id', '=', pick_2.id)])
        self.assertFalse(backorders,
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
        # Invoice view
        result = pick_1.action_view_invoice()
        self.assertEqual(result['views'][0][1], 'form')
        self.assertEqual(result['res_id'], inv_1.id)
        # Mock multiple invoices linked to a picking
        inv_3 = inv_1.copy()
        inv_3.picking_ids |= pick_1
        result = pick_1.action_view_invoice()
        self.assertEqual(result['views'][0][1], 'tree')
