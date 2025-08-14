# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import RecordCapturer

from odoo.addons.stock_split_picking.tests.common import TestStockSplitPickingCase

from ..exceptions import DimensionMustBePositiveError, DimensionRequiredError


class TestStockSplitPickingDimension(TestStockSplitPickingCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # we need to set the dimensions on the product to be able to test the wizard
        # our picking will contain 3 products
        # The first product will have dimensions 10x10x10 = 1000 and weight 10
        # The second product will have dimensions 20x10x10 = 2000 and weight 20
        # The third product will have dimensions 15x10x10 = 1500 and weight 15
        # The total volume will be 10*10*10 + 20*10*10 + 15*10*10 = 4500
        # The total weight will be 10 + 20 + 15 = 45
        cls.product.product_length = 10
        cls.product.product_height = 10
        cls.product.product_width = 10
        cls.product.weight = 10

        cls.product_2.product_length = 20
        cls.product_2.product_height = 10
        cls.product_2.product_width = 10
        cls.product_2.weight = 20

        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Test product 3",
                "product_length": 15,
                "product_height": 10,
                "product_width": 10,
                "weight": 15,
            }
        )
        cls.move_3 = cls._create_stock_move(cls.product_3, cls.picking)
        # To ease tests, we set the quantity of the move to 1
        cls.picking.move_ids.product_uom_qty = 1

    def test_wizard_constrains(self):
        wizard = self.env["stock.split.picking"].with_context(
            active_ids=self.picking.ids
        )
        for nbr_line, volume, weight in [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 1, 1),
        ]:
            self.assertTrue(
                wizard.create(
                    {
                        "mode": "dimensions",
                        "max_nbr_lines": nbr_line,
                        "max_volume": volume,
                        "max_weight": weight,
                    }
                )
            )

        for nbr_line, volume, weight in [
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, -1),
            (1, 0, -1),
        ]:
            with self.assertRaises(DimensionMustBePositiveError):
                wizard.create(
                    {
                        "mode": "dimensions",
                        "max_nbr_lines": nbr_line,
                        "max_volume": volume,
                        "max_weight": weight,
                    }
                )

        with self.assertRaises(DimensionRequiredError):
            wizard.create(
                {
                    "mode": "dimensions",
                    "max_nbr_lines": 0,
                    "max_volume": 0,
                    "max_weight": 0,
                }
            )

        # Constraint is ignored if mode is not "dimensions"
        wizard.create(
            {
                "mode": "move",
                "max_nbr_lines": 0,
                "max_volume": 0,
                "max_weight": 0,
            }
        )

    def test_wizard_split_nbr_lines(self):
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            self._split_picking(
                self.picking,
                mode="dimensions",
                max_nbr_lines=1,
                max_volume=0,
                max_weight=0,
            )
            new_picking = rc.records

        self.assertEqual(new_picking.move_ids, self.move)
        self.assertEqual(self.picking.move_ids, self.move_2 + self.move_3)

    def test_wizard_split_volume(self):
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            self._split_picking(
                self.picking,
                mode="dimensions",
                max_nbr_lines=0,
                max_volume=2600,
                max_weight=0,
            )
            new_picking = rc.records

        # The second move is by passed because it's volume is 2000
        # but the sum of the first and third move is 2500 which is less than 2600
        self.assertEqual(new_picking.move_ids, self.move + self.move_3)
        self.assertEqual(self.picking.move_ids, self.move_2)

    def test_wizard_split_weight(self):
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            self._split_picking(
                self.picking,
                mode="dimensions",
                max_nbr_lines=0,
                max_volume=0,
                max_weight=25,
            )
            new_picking = rc.records

        # The second move is by passed because it's weight is 20
        # but the sum of the first and second move is 30 which is more than 25
        self.assertEqual(new_picking.move_ids, self.move + self.move_3)
        self.assertEqual(self.picking.move_ids, self.move_2)

    def test_wizard_ignore_cancelled_moves(self):
        self.move._action_cancel()

        with RecordCapturer(self.env["stock.picking"], []) as rc:
            self._split_picking(
                self.picking,
                mode="dimensions",
                max_nbr_lines=1,
                max_volume=0,
                max_weight=0,
            )
            new_picking = rc.records

        self.assertEqual(new_picking.move_ids, self.move_2)
        self.assertEqual(self.picking.move_ids, self.move + self.move_3)

    def test_wizard_user_volume_uom(self):
        # The default system volume is cubic meter, but we change it
        # to litre to test the conversion
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create(
                {
                    "mode": "dimensions",
                    "max_nbr_lines": 0,
                    "max_volume": 1,
                    "max_weight": 0,
                    "user_volume_uom_id": self.env.ref("uom.product_uom_litre").id,
                }
            )
        )
        # The max_volume is expressed in the system volume (1 m3)
        # However, the user_max_volume is expressed in the user volume (1000L)
        self.assertAlmostEqual(wizard.user_max_volume, 1000)
        # Setting the user_max_volume should update the max_volume
        wizard.user_max_volume = 2000
        self.assertAlmostEqual(wizard.max_volume, 2)

    def test_wizard_user_weight_uom(self):
        # The default system weight is kg, but we change it
        # to gram to test the conversion
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create(
                {
                    "mode": "dimensions",
                    "max_nbr_lines": 0,
                    "max_volume": 0,
                    "max_weight": 1,
                    "user_weight_uom_id": self.env.ref("uom.product_uom_gram").id,
                }
            )
        )
        # The max_weight is expressed in the system weight (1 kg)
        # However, the user_max_weight is expressed in the user weight (1000g)
        self.assertAlmostEqual(wizard.user_max_weight, 1000)
        # Setting the user_max_weight should update the max_weight
        wizard.user_max_weight = 2000
        self.assertAlmostEqual(wizard.max_weight, 2)
