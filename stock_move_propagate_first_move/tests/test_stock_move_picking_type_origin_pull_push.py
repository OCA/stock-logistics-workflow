# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePickingTypeOriginPullPush(TestStockMovePickingTypeOrigin):
    def test_pull_push_two_steps(self):
        """
        Pull-push rule for reception: pull from Supplier to Input,
        then push from Input to Stock
        """
        self.env["stock.route"].create(
            {
                "name": "Reception: Supplier -> Input -> Stock",
                "sequence": 1,
                "warehouse_selectable": True,
                "warehouse_ids": [Command.link(self.warehouse.id)],
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Supplier -> Input",
                            "action": "pull",
                            "picking_type_id": self.picking_type_in.id,
                            "location_src_id": self.loc_customer.id,
                            "location_dest_id": self.loc_in_1.id,
                            "procure_method": "make_to_stock",
                        },
                    ),
                    Command.create(
                        {
                            "name": "Input -> Stock",
                            "action": "push",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_in_1.id,
                            "location_dest_id": self.loc_stock.id,
                            "auto": "manual",
                        },
                    ),
                ],
            }
        )
        move_in = self.env["stock.move"].create(
            {
                "name": "reception product A",
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.loc_supplier.id,
                "location_dest_id": self.loc_in_1.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )
        move_in._action_confirm()
        move_in.picking_id.button_validate()
        move_store = move_in.move_dest_ids

        self.assertEqual(len(move_store), 1)
        self.assertEqual(move_store.location_id, self.loc_in_1)
        self.assertEqual(move_store.location_dest_id, self.loc_stock)

        self.assertEqual(move_in.picking_type_id, self.picking_type_in)
        self.assertEqual(move_in.first_picking_type_id, self.picking_type_in)
        self.assertEqual(move_in.first_move_id, move_in)

        self.assertEqual(move_store.picking_type_id, self.picking_type_inter)
        self.assertEqual(move_store.first_picking_type_id, self.picking_type_in)
        self.assertEqual(move_store.first_move_id, move_in)
