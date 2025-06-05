# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from .common import CheckoutSyncCommonCase


class TestMoveCommonDestSyncLocation(CheckoutSyncCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.packing_location_1 = cls.env["stock.location"].create(
            {"name": "Packing 1", "location_id": cls.packing_location.id}
        )
        cls.packing_location_2 = cls.env["stock.location"].create(
            {"name": "Packing 2", "location_id": cls.packing_location.id}
        )
        cls.pick_handover_type = cls.warehouse.pick_type_id.copy(
            {"name": "Pick Handover", "sequence_code": "HO"}
        )
        cls.pack_post_type = cls.warehouse.pack_type_id.copy(
            {"name": "Pack Post", "sequence_code": "PPO"}
        )
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_1, 10)
        cls._update_qty_in_location(cls.stock_shelf_location, cls.product_2, 10)
        # Build chains such as we have:
        # PICK
        #  - pick_move1 -> pack_move1
        #  - pick_move2 -> pack_move2
        # PICK_SPECIAL
        #  - pick_move3 -> pack_move3
        # PACK
        #  - pack_move1
        #  - pack_move2
        #  - pack_move3

        cls.pick_move1 = cls._create_single_move(cls.pick_type, cls.product_1)
        cls.pack_move1 = cls._create_single_move(
            cls.pack_type, cls.product_1, move_orig=cls.pick_move1
        )
        cls.pick_move2 = cls._create_single_move(cls.pick_type, cls.product_2)
        cls.pack_move2 = cls._create_single_move(
            cls.pack_type, cls.product_2, move_orig=cls.pick_move2
        )
        cls.pick_move3 = cls._create_single_move(cls.pick_handover_type, cls.product_1)
        cls.pack_move3 = cls._create_single_move(
            cls.pack_type, cls.product_1, move_orig=cls.pick_move3
        )
        cls.moves = moves = (
            cls.pick_move1
            + cls.pack_move1
            + cls.pick_move2
            + cls.pack_move2
            + cls.pick_move3
            + cls.pack_move3
        )
        moves._assign_picking()

        cls.picking_pack = cls.pack_move1.picking_id

    def _prepare_pickings(self, with_check=True):
        self.pack_type.checkout_sync = True
        self.pack_post_type.checkout_sync = True

        if not with_check:
            self.assertTrue(self.pick_move1.picking_id.can_sync_to_checkout)
            self.assertTrue(self.pick_move2.picking_id.can_sync_to_checkout)
            self.assertTrue(self.pick_move3.picking_id.can_sync_to_checkout)

        self.moves._action_assign()
        if not with_check:
            return
        self.assertEqual(self.pick_move1.state, "assigned")
        self.assertEqual(self.pick_move2.state, "assigned")
        self.assertEqual(self.pick_move3.state, "assigned")

    def test_pack_sync(self):
        self._prepare_pickings()
        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        self.assertRecordValues(
            wizard,
            [
                {
                    "picking_ids": self.pick_move1.picking_id.ids,
                    "move_ids": (
                        self.pick_move1 | self.pick_move2 | self.pick_move3
                    ).ids,
                    "dest_picking_id": self.picking_pack.id,
                    "remaining_help": False,
                    "done_dest_picking_ids": [],
                    # False because we do not have other picking to sync after
                    "show_skip_button": False,
                }
            ],
        )
        wizard.location_id = self.packing_location_1
        wizard.sync()

        # Sync updated the destinations
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
            }
        )

    def test_pack_no_sync(self):
        self.pack_type.checkout_sync = False
        self.pack_post_type.checkout_sync = False
        self.assertFalse(self.pick_move1.picking_id.can_sync_to_checkout)
        self.assertFalse(self.pick_move2.picking_id.can_sync_to_checkout)
        self.assertFalse(self.pick_move3.picking_id.can_sync_to_checkout)

    def test_pack_sync_in_2_times(self):
        # In this test, instead of having all the move lines to sync at the
        # same time, we have 1 move line that we put in a selected packing
        # location. Then, we assign the other moves, we expect the new move
        # lines to have the same destination location as the first move.
        # It works because we set the selected location on the other stock.move
        # records, so the move lines inherit the move's destination location
        self._prepare_pickings()
        wizard = self.env["stock.move.checkout.sync"]._create_self(
            self.pick_move1.picking_id
        )
        wizard.location_id = self.packing_location_1
        wizard.sync()

        # Sync updated the destinations on the moves, but we have no move lines
        # yet
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
            }
        )

        (self.pick_move2 | self.pick_move3)._action_assign()
        self.assertEqual(self.pick_move1.state, "assigned")
        self.assertEqual(self.pick_move2.state, "assigned")
        self.assertEqual(self.pick_move3.state, "assigned")

        # same check as before, but it will check the move lines as well
        self.assert_locations(
            {
                # these 3 moves reach the same pack transfer
                self.pick_move1
                | self.pick_move2
                | self.pick_move3: self.packing_location_1,
            }
        )

    def test_skip_to_next(self):
        self._prepare_pickings(with_check=False)
        next_action = self.pick_move1.picking_id.open_checkout_sync_wizard()
        wizard = self.env["stock.move.checkout.sync"].browse(next_action["res_id"])
        next_action = wizard.skip_to_next()
        self.assertFalse(next_action)

    def test_open_checkout_sync_wizard(self):
        self._prepare_pickings(with_check=False)
        next_action = self.pick_move1.picking_id.open_checkout_sync_wizard()
        wizard = self.env["stock.move.checkout.sync"].browse(next_action["res_id"])
        self.assertRecordValues(
            wizard,
            [
                {
                    "picking_ids": self.pick_move1.picking_id.ids,
                    "move_ids": (
                        self.pick_move1 | self.pick_move2 | self.pick_move3
                    ).ids,
                    "dest_picking_id": self.picking_pack.id,
                    "remaining_help": False,
                    "done_dest_picking_ids": [],
                    # False because we do not have other picking to sync after
                    "show_skip_button": False,
                }
            ],
        )
