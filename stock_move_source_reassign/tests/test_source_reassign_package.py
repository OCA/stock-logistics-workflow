# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import MoveSourceReassignCommon


class TestMoveSourceReassignPackage(MoveSourceReassignCommon):
    def test_move_reassign(self):
        self._create_needs()
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
        self.pick_shop._put_in_pack(self.pick_shop.move_line_ids)
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
        self.assertEqual("assigned", self.delivery_shop.state)

        package_level = self.delivery_shop.package_level_ids

        self.assertEqual(1, len(package_level))
        package = package_level.package_id

        package_level.move_line_ids.move_id._source_reassign(
            self.delivery.picking_type_id, self.picking_type_transfer, self.delivery
        )

        transfer_move = self.env["stock.move"].search(
            [("picking_type_id", "=", self.picking_type_transfer.id)]
        )
        self.assertTrue(transfer_move)

        # We ensure the same package is transferred
        transfer_package = transfer_move.move_line_ids.package_level_id.package_id
        self.assertEqual(transfer_package, package)

        transfer_move.move_line_ids.qty_done = 5.0
        transfer_move.picking_id._action_done()
        self.assertEqual("done", transfer_move.picking_id.state)
        self.assertEqual("assigned", self.delivery.state)
