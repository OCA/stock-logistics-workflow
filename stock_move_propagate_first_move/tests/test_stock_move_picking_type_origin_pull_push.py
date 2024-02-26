# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestStockMovePickingTypeOrigin


class TestStockMovePickingTypeOriginPull(TestStockMovePickingTypeOrigin):
    def test_pull_two_steps(self):
        self.warehouse.reception_steps = "three_steps"
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.loc_supplier.id,
                "location_dest_id": self.loc_in_1.id,
                "picking_type_id": self.picking_type_in.id,
                "move_lines": [
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
        moves = self.env["stock.move"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(moves), 3)
        self.assertEqual(moves[0].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[0].picking_type_id, self.picking_type_in)
        self.assertEqual(moves[1].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[1].picking_type_id, self.picking_type_inter)
        self.assertEqual(moves[2].first_picking_type_id, self.picking_type_in)
        self.assertEqual(moves[2].picking_type_id, self.picking_type_inter)
        self.assertEqual(moves[1].first_move_id, moves[0])
        self.assertEqual(moves[2].first_move_id, moves[0])
