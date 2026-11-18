# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from .common import MoveSourceReassignCommon


class TestPickingSourceReassign(MoveSourceReassignCommon):
    def test_picking_reassign(self):
        self._create_needs()
        self.delivery_shop = self.env["stock.picking"].search(
            [
                (
                    "move_ids.rule_id",
                    "=",
                    self.route_shop.rule_ids.filtered(
                        lambda rule: rule.location_src_id == self.shop_out
                    ).id,
                ),
            ]
        )
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
        with self.assertRaises(ValidationError):
            original_move = self.delivery_shop.move_ids[0]
            original_move._source_reassign(
                self.delivery.picking_type_id, self.picking_type_transfer, self.delivery
            )

        self.pick_shop = self.env["stock.picking"].search(
            [
                (
                    "move_ids.rule_id",
                    "=",
                    self.route_shop.rule_ids.filtered(
                        lambda rule: rule.location_src_id == self.warehouse.lot_stock_id
                    ).id,
                ),
            ]
        )
        self.pick_shop.move_line_ids.qty_done = 5.0
        self.pick_shop._action_done()
        self.assertEqual("done", self.pick_shop.state)

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
        self.pick._action_done()
        self.assertEqual("done", self.pick.state)

        self.assertEqual("assigned", self.delivery_shop.state)

        original_move = self.delivery_shop.move_ids[0]

        result = original_move.picking_id.action_source_reassign()

        self.assertEqual("stock.move.reassign", result.get("res_model"))

        wizard = (
            self.env["stock.move.reassign"]
            .with_context(**result.get("context"))
            .create({})
        )
        self.assertEqual("ask_picking_type", wizard.step)
        wizard.reassign_picking_type_id = self.warehouse.out_type_id

        wizard.doit()
        self.assertEqual("ask_destination", wizard.step)
        wizard.doit()
        self.assertEqual("ask_transfer", wizard.step)
        wizard.reassign_transfer_picking_type_id = self.picking_type_transfer
        wizard.doit()
        self.assertEqual("result", wizard.step)

        self.assertEqual(original_move.picking_id, self.delivery)

        transfer_move = self.env["stock.move"].search(
            [("picking_type_id", "=", self.picking_type_transfer.id)]
        )
        self.assertTrue(transfer_move)

        # Transfer the move from SHOP/Out -> Output
        transfer_move.move_line_ids.qty_done = 5.0
        transfer_move.picking_id._action_done()
        self.assertEqual("done", transfer_move.picking_id.state)
        self.assertEqual("assigned", original_move.state)
