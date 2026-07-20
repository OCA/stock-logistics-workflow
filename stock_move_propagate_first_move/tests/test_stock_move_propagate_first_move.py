# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePropagateFirstMove(TestStockMovePickingTypeOrigin):
    def test_first_move_id_not_copied_during_non_chanied_move_split(self):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.loc_supplier.id,
                "location_dest_id": self.loc_in_1.id,
                "picking_type_id": self.picking_type_in.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.loc_supplier.id,
                            "location_dest_id": self.loc_in_1.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()

        picking.move_line_ids.qty_done = 2
        picking._action_done()

        backorder = picking.backorder_ids
        self.assertTrue(backorder, "No backorder picking was created")

        original_move = picking.move_ids
        backorder_move = backorder.move_ids
        self.assertFalse(original_move.first_move_id)
        self.assertFalse(backorder_move.first_move_id)

    def test_first_move_id_well_copied_during_chained_moves_split(self):
        self.warehouse.delivery_steps = "pick_ship"
        pg_out = self.env["procurement.group"].create({"name": "PG Out"})

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

        moves = self.stock_model.search([("group_id", "=", pg_out.id)])
        ship_move = moves.filtered(lambda m: m.picking_type_id == self.picking_type_out)
        pick_move = moves - ship_move

        pick = pick_move.picking_id
        ship = ship_move.picking_id

        # create a backorder on pick
        pick.move_ids.quantity_done = 1
        pick._action_done()
        pick_backorder = pick.backorder_ids
        pick_move_bo = pick_backorder.move_ids

        self.assertEqual(pick_move_bo.first_move_id, ship_move)

        # create a backorder on ship
        ship.move_ids.quantity_done = 1
        ship._action_done()
        ship_backorder = ship.backorder_ids
        ship_move_bo = ship_backorder.move_ids

        self.assertFalse(ship_move_bo.first_move_id)
        self.assertEqual(pick_move_bo.first_move_id, ship_move_bo)
