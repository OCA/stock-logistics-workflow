# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePickingTypeOriginPush(TestStockMovePickingTypeOrigin):
    def test_push_two_steps(self):
        pg_in = self.env["procurement.group"].create({"name": "PG IN"})
        routes = self.env["stock.location.route"].create(
            {
                "name": "Route",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "sequence": 1,
                            "name": "Supplier -> input rule",
                            "action": "pull_push",
                            "picking_type_id": self.picking_type_in.id,
                            "location_src_id": self.loc_supplier.id,
                            "location_id": self.loc_in_1.id,
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 1,
                            "name": "input 1 -> input 2 rule",
                            "action": "push",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_in_1.id,
                            "location_id": self.loc_in_2.id,
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 2,
                            "name": "input 2 -> stock rule",
                            "action": "push",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_in_2.id,
                            "location_id": self.loc_stock.id,
                        },
                    ),
                ],
            }
        )
        self.product.route_ids = routes
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_in_1, 2.0
        )
        self.env["procurement.group"].run(
            [
                pg_in.Procurement(
                    self.product,
                    2.0,
                    self.product.uom_id,
                    self.loc_in_1,
                    "receive product",
                    "receive product",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": pg_in},
                )
            ]
        )
        moves = self.stock_model.search([("group_id", "=", pg_in.id)])
        self.assertEqual(len(moves), 3)
        self.assertEqual(moves[0].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[0].picking_type_id, self.picking_type_in)
        self.assertEqual(moves[1].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[1].picking_type_id, self.picking_type_inter)
        self.assertEqual(moves[2].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[2].picking_type_id, self.picking_type_inter)
        self.assertEqual(moves[1].first_move_id, moves[0])
        self.assertEqual(moves[2].first_move_id, moves[0])
