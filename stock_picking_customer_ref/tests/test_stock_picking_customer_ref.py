# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestStockPickingCustomerRef(common.TransactionCase):

    def setUp(self):
        super(TestStockPickingCustomerRef, self).setUp()
        self.sale_model = self.env['sale.order']
        self.picking_model = self.env['stock.picking']
        product = self.env.ref('product.product_product_19')
        sale_vals = {
            'partner_id': self.env.ref('base.res_partner_2').id,
            'partner_shipping_id': self.env.ref('base.res_partner_2').id,
            'partner_invoice_id': self.env.ref('base.res_partner_2').id,
            'pricelist_id': self.env.ref('product.list0').id}
        sale_line_vals = {
            'product_id': product.id,
            'name': product.name,
            'product_uos_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)
        self.sale_order.with_context(show_sale=True).action_button_confirm()

    def test_stock_picking_customer_ref(self):
        self.sale_order.client_order_ref = 'A-123321'
        cond = [('origin', '=', self.sale_order.name)]
        pickings = self.picking_model.search(cond)
        self.assertNotEqual(
            len(pickings), 0, 'It has not generated the picking  confirming'
            ' the sale order')
        for picking in pickings:
            self.assertEqual(
                picking.client_order_ref, self.sale_order.client_order_ref,
                'Order ref of picking not equal client order ref or sale')
