# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .scaffold_test_objects import ScaffoldTestObjects


class TestStockPicking(ScaffoldTestObjects):

    def setUp(self):
        super(TestStockPicking, self).setUp()
        packages = self.scaffold_stock_quant_package()
        self.parent_p = packages['stock_quant_package_parent']
        self.child_p = packages['stock_quant_package_child']

    def test_compute_package_ids(self):
        """ Test and package_ids correct """
        picking = self.env.ref('stock.outgoing_chicago_warehouse')
        picking.action_confirm()
        picking.force_assign()
        for item in picking.pack_operation_product_ids:
            item.qty_done = 1.0
            item.package_id = self.parent_p
            item.result_package_id = self.child_p
        self.assertIn(
            self.parent_p.id,
            picking.package_ids.ids,
        )
        self.assertIn(
            self.child_p.id,
            picking.package_ids.ids,
        )
