# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import ClusterPickingCommonFeatures


class TestPickingLock(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestPickingLock, cls).setUpClass()
        cls.make_picking_batch.picking_locking_mode = "sql_for_update_skip_locked"

    def test_picking_search_with_lock_mode(self):
        """
        Test the correctness of the picking search with the lock mode
        """
        # by default the wizard initialized will select pick3 as first picking
        # and therefore the device 3. To ensure that all the picks can be added
        # to the batch we need tu update the device 3 to have more bins
        # (default 1)
        self.device3.nbr_bins = 60
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.picks, batch.picking_ids)
        self.assertEqual(self.pick3, self.make_picking_batch._first_picking)
