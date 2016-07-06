# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestStockQuantPackage(TransactionCase):

    def setUp(self):
        super(TestStockQuantPackage, self).setUp()

        self.uom_m = self.env.ref('product.product_uom_meter')
        self.uom_cm = self.env.ref('product.product_uom_cm')
        self.package = self.env['stock.quant.package'].create({
            'length': 10,
            'width': 200,
            'height': 100,
            'dimensional_uom_id': self.uom_m.id,
        })

    def test_calculate_volume_in_cm(self):
        ''' Tests _computes_volume conversion to cm '''
        self.package.dimensional_uom_id = self.uom_cm.id
        self.package._calculate_volume()
        self.assertAlmostEqual(
            0.2,
            self.package.volume,
            'Should be almost equal to 0.2'
        )

    def test_calculate_volume_in_meters(self):
        ''' Tests _computes_volume using meters '''
        self.package._calculate_volume()
        self.assertAlmostEqual(
            200000,
            self.package.volume,
            'Should be almost equal to 200,000'
        )

    def test_calculate_volume_none_dimension(self):
        '''Tests calculate_volume for empty dimensions'''
        self.package.length = None
        self.assertFalse(
            self.package.volume,
            'Volume should be None if one of any dimensions not present',
        )
