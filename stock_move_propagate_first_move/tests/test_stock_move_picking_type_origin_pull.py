# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePickingTypeOriginPull(TestStockMovePickingTypeOrigin):
    def test_pull_two_steps(self):
        """
        Stock -> Output -> Customer
        """
        self.env["stock.route"].create(
            {
                "name": "Stock -> Output -> Customer",
                "warehouse_selectable": True,
                "warehouse_ids": [Command.link(self.warehouse.id)],
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Stock -> Output",
                            "action": "pull",
                            "procure_method": "make_to_stock",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_stock.id,
                            "location_dest_id": self.loc_out.id,
                            "location_dest_from_rule": True,
                        },
                    ),
                    Command.create(
                        {
                            "name": "Output -> Customer",
                            "action": "pull",
                            "procure_method": "make_to_order",
                            "picking_type_id": self.picking_type_out.id,
                            "location_src_id": self.loc_out.id,
                            "location_dest_id": self.loc_customer.id,
                        }
                    ),
                ],
            }
        )
        move_ship = self.env["stock.move"].create(
            {
                "name": "delivery product A",
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "procure_method": "make_to_order",
                "product_uom": self.product.uom_id.id,
                "location_id": self.loc_out.id,
                "location_dest_id": self.loc_customer.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        move_ship._action_confirm()
        move_pick = self.env["stock.move"].search(
            [
                ("location_id", "=", self.loc_stock.id),
                ("location_dest_id", "=", self.loc_out.id),
            ]
        )
        move_ship = self.env["stock.move"].search(
            [
                ("location_id", "=", self.loc_out.id),
                ("location_dest_id", "=", self.loc_customer.id),
            ]
        )
        self.assertEqual(len(move_pick), 1)
        self.assertEqual(len(move_ship), 1)
        self.assertEqual(move_pick.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick.first_move_id, move_ship)
        self.assertEqual(move_pick.picking_type_id, self.picking_type_inter)

        self.assertEqual(move_ship.first_move_id, move_ship)
        self.assertEqual(move_ship.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_ship.picking_type_id, self.picking_type_out)

    def test_pull_three_steps(self):
        """
        Stock -> Output -> Output2 -> Customer
        """
        self.env["stock.route"].create(
            {
                "name": "Stock -> Output -> Output2 -> Customer",
                "warehouse_selectable": True,
                "warehouse_ids": [Command.link(self.warehouse.id)],
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Stock -> Output",
                            "action": "pull",
                            "procure_method": "make_to_stock",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_stock.id,
                            "location_dest_id": self.loc_out.id,
                            "location_dest_from_rule": True,
                        },
                    ),
                    Command.create(
                        {
                            "name": "Output -> Output 2",
                            "action": "pull",
                            "procure_method": "make_to_order",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_out.id,
                            "location_dest_id": self.loc_out_2.id,
                            "location_dest_from_rule": True,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Output -> Customer",
                            "action": "pull",
                            "procure_method": "make_to_order",
                            "picking_type_id": self.picking_type_out.id,
                            "location_src_id": self.loc_out_2.id,
                            "location_dest_id": self.loc_customer.id,
                        }
                    ),
                ],
            }
        )
        move_ship = self.env["stock.move"].create(
            {
                "name": "delivery product A",
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "procure_method": "make_to_order",
                "product_uom": self.product.uom_id.id,
                "location_id": self.loc_out_2.id,
                "location_dest_id": self.loc_customer.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        move_ship._action_confirm()
        move_pick1 = self.env["stock.move"].search(
            [
                ("location_id", "=", self.loc_stock.id),
                ("location_dest_id", "=", self.loc_out.id),
            ]
        )
        move_pick2 = self.env["stock.move"].search(
            [
                ("location_id", "=", self.loc_out.id),
                ("location_dest_id", "=", self.loc_out_2.id),
            ]
        )
        move_ship = self.env["stock.move"].search(
            [
                ("location_id", "=", self.loc_out_2.id),
                ("location_dest_id", "=", self.loc_customer.id),
            ]
        )
        self.assertEqual(len(move_ship), 1)
        self.assertEqual(len(move_pick1), 1)
        self.assertEqual(len(move_pick2), 1)

        self.assertEqual(move_pick1.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick1.first_move_id, move_ship)
        self.assertEqual(move_pick1.picking_type_id, self.picking_type_inter)

        self.assertEqual(move_pick2.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick2.first_move_id, move_ship)
        self.assertEqual(move_pick2.picking_type_id, self.picking_type_inter)

        self.assertEqual(move_ship.first_move_id, move_ship)
        self.assertEqual(move_ship.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_ship.picking_type_id, self.picking_type_out)
