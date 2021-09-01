# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..exceptions import NoSuitableDeviceError
from .common import ClusterPickingCommonFeatures


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestClusteringConditions, cls).setUpClass()
        cls.make_picking_batch = cls.makePickingBatch.create(
            {
                "user_id": cls.env.user.id,
                "picking_type_ids": [(4, cls.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, cls.device1.id),
                    (4, cls.device2.id),
                    (4, cls.device3.id),
                ],
            }
        )
        cls.p5 = cls._create_product("Unittest P5", 1, 4, 1, 1)

    def test_device_with_one_bin(self):
        candidates_pickings = self.make_picking_batch._search_pickings()
        device = self.make_picking_batch._compute_device_to_use(candidates_pickings[0])
        (
            selected_pickings,
            unselected_pickings,
            _,
        ) = self.make_picking_batch._apply_limits(candidates_pickings, device)
        self.assertTrue(selected_pickings)
        self.assertEqual(selected_pickings[0], candidates_pickings[0])

    def test_put_3_pickings_in_one_cluster(self):
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.p1.write(
            {"volume": 5.0, "length": 5, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 5.0, "length": 5, "height": 1, "width": 1, "weight": 1}
        )
        picks = self._get_picks_by_type(self.picking_type_1)
        self._add_product_to_picking(picks[0], self.p5)
        self.make_picking_batch.write({"maximum_number_of_preparation_lines": 6})
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p5
        )
        candidates_pickings = self.make_picking_batch._search_pickings()
        device = self.make_picking_batch._compute_device_to_use(candidates_pickings[0])
        (
            selected_pickings,
            unselected_pickings,
            _,
        ) = self.make_picking_batch._apply_limits(candidates_pickings, device)
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 3)
        self.assertTrue(unselected_pickings)
        self.assertEqual(len(unselected_pickings), 1)

    def test_no_device_for_clustering(self):
        self.p1.write(
            {"volume": 200.0, "length": 200, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 200.0, "length": 200, "height": 1, "width": 1, "weight": 1}
        )
        self.p5.write(
            {"volume": 200.0, "length": 200, "height": 1, "width": 1, "weight": 1}
        )

        self._set_quantity_in_stock(self.stock_location, self.p5)
        picks = self._get_picks_by_type(self.picking_type_1)
        self._add_product_to_picking(picks[0], self.p5)
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p5
        )
        candidates_pickings = self.make_picking_batch._search_pickings()
        for picking in candidates_pickings:
            device = self.make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        self.assertFalse(device)

        with self.assertRaises(NoSuitableDeviceError):
            self.make_picking_batch._create_batch(raise_if_not_possible=True)

    def test_one_picking_on_another_device(self):
        self.p1.write(
            {"volume": 10.0, "length": 10, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 10.0, "length": 10, "height": 1, "width": 1, "weight": 1}
        )
        self.p5.write(
            {"volume": 120.0, "length": 120, "height": 1, "width": 1, "weight": 1}
        )
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.device1.write({"nbr_bins": 8})
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p5, priority="0"
        )
        pick_on_another_device = self.env["stock.picking"].search(
            [("product_id", "=", self.p5.id)]
        )
        candidates_pickings = self.make_picking_batch._search_pickings()
        device = self.make_picking_batch._compute_device_to_use(candidates_pickings[0])
        (
            selected_pickings,
            unselected_pickings,
            _,
        ) = self.make_picking_batch._apply_limits(candidates_pickings, device)
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 3)
        self.assertTrue(unselected_pickings)
        self.assertEqual(len(unselected_pickings), 1)
        self.assertEqual(unselected_pickings, pick_on_another_device)

    def test_put_2_pickings_with_volume_zero_in_one_cluster(self):
        """2 products don't have a volume :
        they should still occupy at least one bin each"""
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": 200,
                "nbr_bins": 6,
                "sequence": 50,
            }
        )
        make_picking_batch_volume_zero = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [(4, device.id)],
            }
        )
        self.p1.write(
            {"volume": 0.0, "length": 0, "height": 0, "width": 0, "weight": 1}
        )
        self.p2.write(
            {"volume": 0.0, "length": 0, "height": 0, "width": 0, "weight": 1}
        )
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p2
        )
        make_picking_batch_volume_zero.write({"maximum_number_of_preparation_lines": 6})
        candidates_pickings = make_picking_batch_volume_zero._search_pickings()
        device = make_picking_batch_volume_zero._compute_device_to_use(
            candidates_pickings[0]
        )
        batch = make_picking_batch_volume_zero._create_batch()
        selected_pickings = batch.picking_ids
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 4)

        # All picks have a volume of 0 : they should each occupy one bin
        self.assertEqual(batch.wave_nbr_bins, len(selected_pickings))

    def test_user_propagates_on_pickings(self):
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch.picking_ids)
        self.assertEqual(batch.user_id.id, self.env.user.id)
        for pick in batch.picking_ids:
            self.assertEqual(pick.user_id.id, self.env.user.id)

        # remove user_id from batch
        batch.user_id = False
        for pick in batch.picking_ids:
            self.assertFalse(pick.user_id)

    def test_only_available_moves_for_weight_and_volume(self):
        total_weight_pickings = 0
        total_volume_pickings = 0
        self.p3.write(
            {"volume": 10.0, "length": 10, "height": 1, "width": 1, "weight": 1}
        )
        self.p4.write(
            {"volume": 10.0, "length": 10, "height": 1, "width": 1, "weight": 1}
        )
        self.p5.write(
            {"volume": 10.0, "length": 10, "height": 1, "width": 1, "weight": 1}
        )
        self._create_picking_pick_and_assign(
            self.picking_type_2.id, products=self.p3 | self.p4 | self.p5
        )
        picks = self._get_picks_by_type(self.picking_type_2)
        pick = picks.filtered(lambda p: len(p.move_lines) == 3)
        move_line = pick.move_lines[0]
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_2.id)],
                "stock_device_type_ids": [
                    (4, self.device4.id),
                    (4, self.device5.id),
                    (4, self.device6.id),
                ],
            }
        )
        batch = make_picking_batch._create_batch()
        self.assertTrue(batch.picking_ids)
        for pick in batch.picking_ids:
            for move_line in pick.move_lines:
                total_weight_pickings += move_line.product_id.weight
                total_volume_pickings += move_line.product_id.volume
        move_line_volume = move_line.product_id.volume
        move_line_weight = move_line.product_id.weight
        self.assertEqual(batch.wave_volume, total_volume_pickings - move_line_volume)
        self.assertEqual(batch.wave_weight, total_weight_pickings - move_line_weight)

    def test_several_pickings_one_partner_one_bin_occupied(self):
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )

        batch = self.make_picking_batch._create_batch()
        selected_pickings = batch.picking_ids
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 3)
        self.assertEqual(batch.wave_nbr_bins, 1)

    def test_several_pickings_one_partner_two_bin_occupied(self):
        self.device3.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 35.0, "length": 35, "height": 1, "width": 1, "weight": 1}
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )

        batch = self.make_picking_batch._create_batch()
        selected_pickings = batch.picking_ids
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 3)
        self.assertEqual(batch.wave_nbr_bins, 2)

    def test_several_pickings_two_partner_two_bin_occupied(self):
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        partner2 = self.env["res.partner"].create(
            {"name": "other partner", "ref": "98098769876"}
        )
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1, partner=partner2
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )

        batch = self.make_picking_batch._create_batch()
        selected_pickings = batch.picking_ids
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 4)
        self.assertEqual(batch.wave_nbr_bins, 2)

    def test_several_pickings_one_partner_volume_outreached_on_one_picking(self):

        self.p1.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.p2.write(
            {"volume": 1.0, "length": 1, "height": 1, "width": 1, "weight": 1}
        )
        self.p5.write(
            {"volume": 200.0, "length": 200, "height": 1, "width": 1, "weight": 1}
        )

        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 30})
        self._create_picking_pick_and_assign(self.picking_type_1.id, products=self.p5)
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p2
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 10,
                "group_pickings_by_partner": True,
            }
        )
        picks = self._get_picks_by_type(self.picking_type_1)
        self.assertEqual(len(picks), 5)
        batch = self.make_picking_batch._create_batch()
        selected_pickings = batch.picking_ids
        self.assertTrue(selected_pickings)
        self.assertEqual(len(selected_pickings), 4)
        self.assertEqual(batch.wave_nbr_bins, 2)
