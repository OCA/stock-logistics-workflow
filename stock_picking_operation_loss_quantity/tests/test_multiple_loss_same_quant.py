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
        self.assertEqual(quant.lock_move_ids.product_uom_qty, 93)
        self.assertEqual(quant.available_quantity, 0)
        self.assertEqual(self.pickings[2].move_line_ids.reserved_uom_qty, 5)
        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(loss_picking.move_ids, quant.lock_move_ids)

    def _get_quant(self, product):
        return self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.loc_stock.id),
            ],
            limit=1,
        )

    def test_loss_preserves_other_pickings_reservations(self):
        first_line = self.pickings[0].move_line_ids
        first_line.qty_done = 1
        first_line.action_lose_quantity()

        for picking in self.pickings[1:]:
            self.assertEqual(picking.state, "assigned")
            self.assertEqual(picking.move_line_ids.reserved_uom_qty, 5)
        quant = self._get_quant(self.product_2)
        # 1 done + 2 x 5 reserved by the other pickings + 89 locked
        self.assertEqual(quant.reserved_quantity, 100)

    def test_loss_on_over_reserved_quant(self):
        # The quant quantity is lower than the reserved quantity
        self._create_quantities(self.product_3, 10.0)
        pickings = self.env["stock.picking"]
        for _ in range(2):
            picking = self.pickings[0].copy()
            picking.move_ids.product_id = self.product_3
            picking.action_assign()
            pickings |= picking
        quant = self._get_quant(self.product_3)
        self.env["stock.quant"]._update_available_quantity(
            self.product_3, self.loc_stock, -8.0
        )
        self.assertEqual(quant.quantity, 2)
        self.assertEqual(quant.reserved_quantity, 10)

        pickings[0].move_line_ids.action_lose_quantity()

        self.assertEqual(pickings[1].move_line_ids.reserved_uom_qty, 5)
        self.assertFalse(pickings[0].move_line_ids)
        self.assertFalse(quant.lock_move_ids)
