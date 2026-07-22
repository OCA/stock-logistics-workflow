# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import MoveSourceReassignCommon


class TestMoveSourceReassignSubLocation(MoveSourceReassignCommon):
    def test_move_reassign(self):
        self._create_needs(delivery_only=True)
        self.pick = self.env["stock.picking"].search(
            [
                (
                    "move_ids.rule_id",
                    "=",
                    self.warehouse.delivery_route_id.rule_ids.filtered(
                        lambda rule: rule.location_src_id == self.warehouse.lot_stock_id
                    ).id,
                ),
            ]
        )
        self.pick.move_line_ids.qty_done = 5.0
        self.pick._action_done()
        self.assertEqual("done", self.pick.state)

        self.pick = self.env["stock.picking"].search(
            [
                (
                    "move_ids.rule_id",
                    "=",
                    self.warehouse.delivery_route_id.rule_ids.filtered(
                        lambda rule: rule.location_src_id == self.warehouse.lot_stock_id
                    ).id,
                ),
            ]
        )
        self.assertTrue(self.pick)
        self.pick.move_line_ids.qty_done = 5.0
        self.pick.move_line_ids.location_dest_id = self.output_2
        self.pick._action_done()
        self.assertEqual("done", self.pick.state)

        self.delivery = self.env["stock.picking"].search(
            [
                ("product_id", "=", self.product_a.id),
                (
                    "move_ids.rule_id",
                    "=",
                    self.warehouse.delivery_route_id.rule_ids.filtered(
                        lambda rule: rule.location_dest_id == self.customers
                    ).id,
                ),
            ]
        )
        delivery_move_before = self.env["stock.move"].search(
            [
                ("picking_type_id.code", "=", "outgoing"),
                ("product_id", "=", self.product_a.id),
            ]
        )
        self.assertEqual(1, len(delivery_move_before))
        picking_before = delivery_move_before.picking_id
        delivery_move_before._source_reassign(
            self.delivery.picking_type_id, self.picking_type_transfer
        )

        self.assertNotEqual(picking_before, delivery_move_before.picking_id)

        transfer_move = self.env["stock.move"].search(
            [
                ("picking_type_id", "=", self.picking_type_transfer.id),
                ("product_id", "=", self.product_a.id),
            ]
        )
        self.assertTrue(transfer_move)
        self.assertEqual("assigned", transfer_move.state)

        self.assertEqual("confirmed", delivery_move_before.state)

        transfer_move.move_line_ids.qty_done = 5.0
        transfer_move.move_line_ids.location_dest_id = self.output_1

        transfer_move._action_done()

        self.assertEqual("assigned", delivery_move_before.state)
