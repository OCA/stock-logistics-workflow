# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_operation_destination_suggestion.tests.common import (
    PickingDestinationSuggestCommon,
)


class TestPickingDestinationSuggest(PickingDestinationSuggestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel_1 = cls.env["stock.release.channel"].create(
            {
                "name": "TEST 1",
            }
        )
        cls.channel_2 = cls.env["stock.release.channel"].create(
            {
                "name": "TEST 2",
            }
        )
        cls.warehouse.pick_type_id.suggest_destination = True
        cls.warehouse.pick_type_id.suggest_destination_partner = False
        cls.warehouse.pick_type_id.suggest_destination_release_channel = True

    def test_picking_suggest(self):
        self._create_procurement()
        self.move_pick_1 = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("state", "=", "assigned"),
            ]
        )
        self.move_pick_1.move_dest_ids.picking_id.release_channel_id = self.channel_1
        self.assertTrue(self.move_pick_1)
        self.move_pick_1.move_line_ids.qty_done = 5.0
        # Put products in a particular location
        location_1 = self.env["stock.location"].search([("barcode", "=", "L#OUT.1")])
        self.move_pick_1.move_line_ids.location_dest_id = location_1
        self.move_pick_1._action_done()

        self.move_out = self.env["stock.move"].search(
            [("location_id", "=", self.output.id), ("product_id", "=", self.product.id)]
        )

        self.assertTrue(self.move_out)
        self.assertTrue(self.move_out.move_line_ids)

        group = self.env["procurement.group"].create(
            {
                "name": "Group 2",
            }
        )
        self._create_procurement(group_id=group)
        self.move_pick_2 = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("state", "=", "assigned"),
            ]
        )
        self.move_pick_2.move_dest_ids.picking_id.release_channel_id = self.channel_2
        self.assertTrue(self.move_pick_2)
        self.assertFalse(
            self.move_pick_2.picking_id.destination_location_suggestion_ids
        )

        # Change Release Channel
        self.move_pick_2.move_dest_ids.picking_id.release_channel_id = self.channel_1
        self.move_pick_2.picking_id.invalidate_recordset()
        self.assertEqual(
            location_1, self.move_pick_2.picking_id.destination_location_suggestion_ids
        )
