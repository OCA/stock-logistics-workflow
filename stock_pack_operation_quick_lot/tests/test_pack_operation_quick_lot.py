# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase


class PackOperationQuickLotCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(PackOperationQuickLotCase, cls).setUpClass()
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.picking_type_in.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'type': 'product',
            'tracking': 'lot',
        })
        cls.env['stock.move'].create({
            'name': 'a move',
            'product_id': cls.product.id,
            'product_uom_qty': 5.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
        })
        cls.picking.action_assign()
        cls.operation = cls.picking.pack_operation_ids[:1]

    def test_quick_input(self):
        self.assertTrue(self.operation)
        self.operation.write({
            'lot_name': 'SN99999999999',
            'life_date': '2030-12-31',
        })
        lot = self.operation.pack_lot_ids[:1].lot_id
        self.assertTrue(lot)
        self.operation.lot_name = 'SN99999999998'
        lot2 = self.operation.pack_lot_ids[:1].lot_id
        self.assertNotEqual(lot, lot2)
        self.operation.life_date = '2030-12-28'
        self.assertEqual(lot2.life_date, '2030-12-28 00:00:00')
        self.assertAlmostEqual(self.operation.qty_done, 5.0)
