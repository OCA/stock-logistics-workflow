# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import ClusterPickingCommonFeatures


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p5 = cls._create_product("Unittest P5", 1, 4, 1, 1)
        cls.batch_profile = cls.env["stock.picking.batch.creation.profile"].create(
            {
                "name": "Test",
                "maximum_number_of_preparation_lines": 40,
            }
        )

    def test_device_wizard_with_profile(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        The first picking will be pick3 (higher priority) and its volume is
        is 30m3. -> device3 is the device to use (min 30m3, max 100m3)

        Device3 has 1 bin -> the batch should only contain pick3
        """
        wizard = self.batch_profile._create_wizard()
        self.assertEqual(40, wizard.maximum_number_of_preparation_lines)
        res = self.batch_profile.action_launch_wizard()
        self.assertEqual(res["res_model"], "make.picking.batch")

    def test_action_menu(self):
        action = self.env["make.picking.batch"].action_launch_picking_batch()
        self.assertEqual(
            "make.picking.batch.profile",
            action["res_model"],
        )
        self.batch_profile.active = False
        action = self.env["make.picking.batch"].action_launch_picking_batch()
        self.assertEqual(
            "make.picking.batch",
            action["res_model"],
        )
