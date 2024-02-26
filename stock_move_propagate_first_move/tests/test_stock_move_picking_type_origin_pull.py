# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePickingTypeOriginPull(TestStockMovePickingTypeOrigin):
    def test_pull_two_steps(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, 10.0
        )
        self.warehouse.delivery_steps = "pick_ship"
        pg_inter = self.env["procurement.group"].create({"name": "PG Inter"})
        pg_out = self.env["procurement.group"].create({"name": "PG Out"})
        routes = self.env["stock.location.route"].create(
            {
                "name": "Route",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_stock.id,
                            "location_id": self.loc_out.id,
                            "group_propagation_option": "fixed",
                            "group_id": pg_inter.id,
                        },
                    )
                ],
            }
        )
        self.product.route_ids = routes
        self.env["procurement.group"].run(
            [
                pg_out.Procurement(
                    self.product,
                    2.0,
                    self.product.uom_id,
                    self.loc_customer,
                    "delivery product A",
                    "delivery product A",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": pg_out},
                )
            ]
        )
        move_pick = self.stock_model.search([("group_id", "=", pg_inter.id)])
        move_ship = self.stock_model.search([("group_id", "=", pg_out.id)])

        self.assertEqual(move_pick.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick.first_move_id, move_ship)
        self.assertEqual(move_pick.picking_type_id, self.picking_type_inter)

        self.assertEqual(move_ship.first_move_id, move_ship)
        self.assertEqual(move_ship.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_ship.picking_type_id, self.picking_type_out)

    def test_pull_three_steps(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, 10.0
        )
        loc_out_2 = self.loc_out.copy({"name": "Output 2"})
        pg_inter_1 = self.env["procurement.group"].create({"name": "PG Inter 1"})
        pg_inter_2 = self.env["procurement.group"].create({"name": "PG Inter 2"})
        pg_out = self.env["procurement.group"].create({"name": "PG Out"})
        routes = self.env["stock.location.route"].create(
            {
                "name": "Route",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "sequence": 1,
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_stock.id,
                            "location_id": self.loc_out.id,
                            "group_propagation_option": "fixed",
                            "group_id": pg_inter_1.id,
                            "procure_method": "make_to_stock",
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 2,
                            "name": "output -> output 2 rule",
                            "action": "pull",
                            "picking_type_id": self.picking_type_inter.id,
                            "location_src_id": self.loc_out.id,
                            "location_id": loc_out_2.id,
                            "group_propagation_option": "fixed",
                            "group_id": pg_inter_2.id,
                            "procure_method": "make_to_order",
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 3,
                            "name": "output 2 -> customer rule",
                            "action": "pull",
                            "picking_type_id": self.picking_type_out.id,
                            "location_src_id": loc_out_2.id,
                            "location_id": self.loc_customer.id,
                            "group_propagation_option": "fixed",
                            "group_id": pg_out.id,
                            "procure_method": "make_to_order",
                        },
                    ),
                ],
            }
        )
        self.product.route_ids = routes
        self.env["procurement.group"].run(
            [
                pg_out.Procurement(
                    self.product,
                    2.0,
                    self.product.uom_id,
                    self.loc_customer,
                    "delivery product A",
                    "delivery product A",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": pg_out},
                )
            ]
        )
        move_ship = self.stock_model.search([("group_id", "=", pg_out.id)])
        move_pick_1 = self.stock_model.search([("group_id", "=", pg_inter_1.id)])
        move_pick_2 = self.stock_model.search([("group_id", "=", pg_inter_2.id)])

        self.assertEqual(move_pick_1.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick_1.picking_type_id, self.picking_type_inter)
        self.assertEqual(move_pick_1.first_move_id, move_ship)

        self.assertEqual(move_pick_2.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_pick_2.picking_type_id, self.picking_type_inter)
        self.assertEqual(move_pick_2.first_move_id, move_ship)

        self.assertEqual(move_ship.first_move_id, move_ship)
        self.assertEqual(move_ship.first_picking_type_id, self.picking_type_out)
        self.assertEqual(move_ship.picking_type_id, self.picking_type_out)
