# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import UserError
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockLotScrap(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockLotScrap, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.lot010 = cls.env['stock.production.lot'].create({
            'name': "0000010",
            'product_id': cls.product.id
        })
        cls.quant1 = cls.env['stock.quant'].create({
            'qty': 5000.0,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'product_id': cls.product.id,
            'lot_id': cls.lot010.id,
        })
        cls.quant2 = cls.env['stock.quant'].create({
            'qty': 325.0,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'product_id': cls.product.id,
            'lot_id': cls.lot010.id,
        })

    def test_picking_created(self):
        res = self.lot010.action_scrap_lot()
        self.assertTrue('res_id' in res)
        picking = self.env['stock.picking'].browse(res['res_id'])
        self.assertEqual(len(picking.move_lines), 2)
        self.assertAlmostEqual(
            sum(picking.move_lines.mapped('product_qty')), 5325)
        self.assertTrue(
            all(picking.move_lines.mapped(lambda x: x.state == 'assigned')))

    def test_warning(self):
        product_new = self.product.create({
            'name': 'Test product 040',
        })
        self.lot040 = self.env['stock.production.lot'].create({
            'name': "0000040",
            'product_id': product_new.id,
        })
        with self.assertRaises(UserError):
            self.lot040.action_scrap_lot()
