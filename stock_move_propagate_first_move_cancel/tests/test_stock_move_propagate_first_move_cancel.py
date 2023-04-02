# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_move_propagate_first_move.tests.common import (
    TestStockMovePickingTypeOrigin,
)


class TestStockMovePropagateFirstMoveCancel(TestStockMovePickingTypeOrigin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 10.0
        )
        loc_out_2 = cls.loc_out.copy({"name": "Output 2"})
        pg_inter_1 = cls.env["procurement.group"].create({"name": "PG Inter 1"})
        pg_inter_2 = cls.env["procurement.group"].create({"name": "PG Inter 2"})
        pg_out = cls.env["procurement.group"].create({"name": "PG Out"})
        routes = cls.env["stock.route"].create(
            {
                "name": "Route",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "sequence": 1,
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": cls.picking_type_inter.id,
                            "location_src_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_out.id,
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
                            "picking_type_id": cls.picking_type_inter.id,
                            "location_src_id": cls.loc_out.id,
                            "location_dest_id": loc_out_2.id,
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
                            "picking_type_id": cls.picking_type_out.id,
                            "location_src_id": loc_out_2.id,
                            "location_dest_id": cls.loc_customer.id,
                            "group_propagation_option": "fixed",
                            "group_id": pg_out.id,
                            "procure_method": "make_to_order",
                        },
                    ),
                ],
            }
        )
        cls.product.route_ids = routes
        cls.env["procurement.group"].run(
            [
                pg_out.Procurement(
                    cls.product,
                    2.0,
                    cls.product.uom_id,
                    cls.loc_customer,
                    "delivery product A",
                    "delivery product A",
                    cls.warehouse.company_id,
                    {"warehouse_id": cls.warehouse, "group_id": pg_out},
                )
            ]
        )
        cls.move_ship = cls.stock_model.search([("group_id", "=", pg_out.id)])
        cls.move_pick_1 = cls.stock_model.search([("group_id", "=", pg_inter_1.id)])
        cls.move_pick_2 = cls.stock_model.search([("group_id", "=", pg_inter_2.id)])
        cls.moves = cls.move_ship | cls.move_pick_1 | cls.move_pick_2

    def test_00(self):
        """all moves are canceled if outgoing move is canceled"""
        self.assertSetEqual(set(self.moves.mapped("state")), {"waiting", "assigned"})
        self.move_ship._action_cancel()
        self.assertSetEqual(set(self.moves.mapped("state")), {"cancel"})

    def test_01(self):
        """the cancellation of pick don't trigger the cancel of all teh chain"""
        self.assertSetEqual(set(self.moves.mapped("state")), {"waiting", "assigned"})
        self.move_pick_1._action_cancel()
        self.assertEqual(self.move_ship.state, "waiting")
        self.assertEqual(self.move_pick_1.state, "cancel")
        self.assertEqual(self.move_pick_2.state, "waiting")

    def test_02(self):
        """all moves are canceled if second pick move is canceled"""
        self.assertSetEqual(set(self.moves.mapped("state")), {"waiting", "assigned"})
        self.move_pick_2._action_cancel()
        self.assertEqual(self.move_ship.state, "waiting")
        self.assertEqual(self.move_pick_1.state, "assigned")
        self.assertEqual(self.move_pick_2.state, "cancel")
