# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import OperationLossQuantityCommon


class TestMultipleLossSameQuant(OperationLossQuantityCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._create_quantities(cls.product_2, 100.0)

        cls.pickings = []
        for _ in range(3):
            picking = cls.env["stock.picking"].create(
                {
                    "picking_type_id": cls.pick_type_out.id,
                    "location_id": cls.loc_stock.id,
                    "location_dest_id": cls.loc_customer.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": "Test Move",
                                "product_id": cls.product_2.id,
                                "product_uom_qty": 5,
                                "location_id": cls.loc_stock.id,
                                "location_dest_id": cls.loc_customer.id,
                            }
                        )
                    ],
                }
            )
            picking.action_assign()
            cls.pickings.append(picking)

    def test_one_single_loss_picking_for_same_quant(self):
        first_line = self.pickings[0].move_line_ids
        first_line.qty_done = 1
        first_line.action_lose_quantity()

        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", self.loc_stock.id),
            ],
            limit=1,
        )
        self.assertTrue(quant.is_locked_by_picking)
        self.assertEqual(quant.lock_move_count, 1)
        self.assertEqual(quant.available_quantity, 0)

        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertTrue(loss_picking.move_ids.filtered("quant_lock_quant_id"))

    def test_repeated_loss_on_same_quant_extends_lock(self):
        first_line = self.pickings[0].move_line_ids
        first_line.qty_done = 1
        first_line.action_lose_quantity()
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", self.loc_stock.id),
            ],
            limit=1,
        )
        # 3 pickings x 5 reserved, 4 released by the first loss
        self.assertEqual(quant.lock_move_ids.product_uom_qty, 89)

        second_line = self.pickings[1].move_line_ids
        second_line.qty_done = 1
        second_line.action_lose_quantity()

        # The quantity released by the second loss is locked as well
        self.assertEqual(second_line.reserved_uom_qty, 1)
        self.assertEqual(sorted(quant.lock_move_ids.mapped("product_uom_qty")), [4, 89])
        self.assertEqual(quant.available_quantity, 0)
        self.assertEqual(self.pickings[2].move_line_ids.reserved_uom_qty, 5)
        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(loss_picking.move_ids, quant.lock_move_ids)
