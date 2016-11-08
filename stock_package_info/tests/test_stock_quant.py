# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .scaffold_test_objects import ScaffoldTestObjects


class TestStockQuant(ScaffoldTestObjects):

    def setUp(self):
        super(TestStockQuant, self).setUp()
        self.quant_obj = self.scaffold_stock_quant()

    def test_compute_totals(self):
        """ Test and total_volume and total_weight correct """
        self.assertEqual(
            [40, 60, 40],
            [
                self.quant_obj.total_volume,
                self.quant_obj.total_weight,
                self.quant_obj.total_weight_net,
            ],
        )
