# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .scaffold_test_objects import ScaffoldTestObjects


class TestStockQuantPackage(ScaffoldTestObjects):
    """ It provides tests for stock.quant.package
    Note that the stored computational methods were showing up as untested
    in coverage, so the computational method that is associated with an assert
    is below it, so as to trick the system while not affecting results.
    I think the most idiotic part about this issue is that once resolving,
    instead of 0 hits per method there are now two (╯°□°)╯︵ ┻━┻
    """

    def setUp(self):
        super(TestStockQuantPackage, self).setUp()
        packages = self.scaffold_stock_quant_package()
        self.parent_package = packages['stock_quant_package_parent']

    def test_compute_total_weights(self):
        """ It should sum totals of quant_ids weights in package """
        self.assertListEqual(
            [120, 80],
            [
                self.parent_package.total_weight,
                self.parent_package.total_weight_net,
            ],
        )
        self.parent_package._compute_total_weights()

    def test_compute_total_est_weight(self):
        """ It should sum totals of self + children_ids weights """
        self.assertListEqual(
            [248, 248],
            [
                self.parent_package.total_est_weight,
                self.parent_package.real_weight,
            ],
        )
        self.parent_package._compute_total_est_weights()

    def test_compute_total_est_weight_net(self):
        """ It should sum totals of self + children_ids net weights """
        self.assertEqual(
            168,
            self.parent_package.total_est_weight_net,
        )
        self.parent_package._compute_total_est_weight_net()

    def test_compute_permitted_volume(self):
        """ It should calculate parent package's permitted_volume correct """
        self.assertEqual(
            6,
            self.parent_package.permitted_volume,
        )
        self.parent_package._compute_permitted_volume()

    def test_compute_total_volume(self):
        """ It should sum totals of quant_ids volume """
        self.assertEqual(
            80,
            self.parent_package.total_volume,
        )
        self.parent_package._compute_total_volume()

    def test_compute_total_volume_charge(self):
        """ It should sum totals of self + childrens volume """
        self.assertEqual(
            160,
            self.parent_package.total_volume_charge,
        )
        self.parent_package._compute_total_volume_charge()

    def test_dimensions(self):
        """ It should inherit dimensions from onchange_product_pack_tmpl_id """
        self.parent_package.onchange_product_pack_tmpl_id()
        self.assertListEqual(
            [1, 3, 2, 4],
            [
                self.parent_package.length,
                self.parent_package.width,
                self.parent_package.height,
                self.parent_package.empty_weight,
            ],
        )

    def test_compute_picking_ids(self):
        """ It should properly assign picking Ids from pack ops """
        pack_ops = self.env['stock.pack.operation'].search([
            ('result_package_id', '=', self.parent_package.id)
        ])
        self.assertEqual(
            pack_ops.mapped('picking_id'), self.parent_package.picking_ids,
        )
        self.parent_package._compute_picking_ids()
