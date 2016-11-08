# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .scaffold_test_objects import ScaffoldTestObjects


class TestStockPicking(ScaffoldTestObjects):

    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.picking = self.scaffold_stock_quant()

    def test_compute_package_ids(self):
        """ Test and package_ids correct """
        picking = self.env.ref('stock.outgoing_chicago_warehouse')
        picking.action_confirm()
        picking.force_assign()
        for item in picking.pack_operation_product_ids:
            item.qty_done = 1.0
        pack_id = picking.put_in_pack()
        self.assertIn(
            pack_id.id,
            picking.package_ids.ids
        )
