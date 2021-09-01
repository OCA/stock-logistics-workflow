# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ClusterPickingCommonFeatures


class TestGetPickingsToCluster(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestGetPickingsToCluster, cls).setUpClass()

    def test_search_and_order_candidates_pickings(self):
        """
        Data: 3 picks in first area
        TestCase: Create a cluster for this area
        Result: retrieve all pickings related to the area,
        check that they are properly sorted
        """
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        self.assertEqual(len(candidates_pickings), 3)
