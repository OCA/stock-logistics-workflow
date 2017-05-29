# -*- coding: utf-8 -*-
# © 2015 Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
import operator


class TestPickingToPackOps(TransactionCase):

    def test_one_move_takes_owner_from_move(self):
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = self._move_factory(product=self.product1,
                                             owner=self.partner2)

        pick.action_confirm()
        result = pick._prepare_pack_ops(self.env['stock.quant'],
                                        {self.product1: 5.0})

        self.assertEqual(1, len(result))
        self.assertEqual(self.partner2.id, result[0]['owner_id'])

    def test_two_moves_same_owner_are_grouped(self):
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = (
            self._move_factory(product=self.product1, owner=self.partner2) |
            self._move_factory(product=self.product1, owner=self.partner2,
                               qty=2.0)
        )

        pick.action_confirm()
        result = pick._prepare_pack_ops(self.env['stock.quant'],
                                        {self.product1: 7.0})

        self.assertEqual(1, len(result))
        self.assertEqual(self.partner2.id, result[0]['owner_id'])
        self.assertAlmostEqual(7.0, result[0]['product_qty'])

    def test_two_moves_two_owners_are_not_grouped(self):
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = (
            self._move_factory(product=self.product1, owner=self.partner1) |
            self._move_factory(product=self.product1, owner=self.partner2,
                               qty=7.0)
        )

        pick.action_confirm()
        result = pick._prepare_pack_ops(self.env['stock.quant'],
                                        {self.product1: 12.0})

        self.assertEqual(2, len(result))
        result.sort(key=operator.itemgetter('product_qty'))
        self.assertEqual(self.partner1.id, result[0]['owner_id'])
        self.assertEqual(self.partner2.id, result[1]['owner_id'])
        self.assertAlmostEqual(5.0, result[0]['product_qty'])
        self.assertAlmostEqual(7.0, result[1]['product_qty'])

    def test_one_move_to_action_done_to_quant(self):
        """action_done is maybe obsolete, but we test it nonetheless.

        This already propagates the owner from the move in the stock module.

        """
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = self._move_factory(product=self.product1,
                                             owner=self.partner2)
        pick.action_done()

        new_quant = self.Quant.search([('product_id', '=', self.product1.id)])
        self.assertEqual(1, len(new_quant))
        self.assertEqual(self.partner2, new_quant.owner_id)

    def test_one_move_to_prepare_partial_do_transfer_to_quant(self):
        """prepare_partial and do_transfer are the methods used when you pass
        from the 'Transfer Details' wizard.

        """
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = self._move_factory(product=self.product1,
                                             owner=self.partner2)
        pick.action_confirm()
        pick.do_prepare_partial()
        pick.do_transfer()

        new_quant = self.Quant.search([('product_id', '=', self.product1.id)])
        self.assertEqual(1, len(new_quant))
        self.assertEqual(self.partner2, new_quant.owner_id)

    def _picking_factory(self, owner):
        return self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_14').id,
            'owner_id': owner.id,
        })

    def _move_factory(self, product, owner, qty=5.0):
        return self.env['stock.move'].create({
            'name': '/',
            'restrict_partner_id': owner.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })

    def setUp(self):
        super(TestPickingToPackOps, self).setUp()
        self.product1 = self.env.ref('product.product_product_4')
        self.product2 = self.env.ref('product.product_product_8')
        self.partner1 = self.env.ref('base.res_partner_1')
        self.partner2 = self.env.ref('base.res_partner_2')

        self.Quant = self.env['stock.quant']
        self.assertFalse(self.Quant.search([('product_id', '=',
                                             self.product1.id)]))
        self.assertFalse(self.Quant.search([('product_id', '=',
                                             self.product2.id)]))
