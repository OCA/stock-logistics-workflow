# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestSalePickingBackToDraft(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestSalePickingBackToDraft, self).setUp(*args, **kwargs)
        self.product_12 = self.env.ref('product.product_product_12')

    def test_sale_picking_back_to_draft(self):
        self.order1 = self.env['sale.order'].create(
            {
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
        self.sol1 = self.env['sale.order.line'].create({
            'name': 'sol1',
            'order_id': self.order1.id,
            'product_id': self.product_12.id,
            'product_uom_qty': 1,
        })
        self.order1.action_button_confirm()
        self.order1.picking_ids.action_cancel()
        self.assertEqual(self.order1.state, 'shipping_except')
        self.order1.picking_ids.action_back_to_draft()
        self.assertEqual(self.order1.state, 'manual')
