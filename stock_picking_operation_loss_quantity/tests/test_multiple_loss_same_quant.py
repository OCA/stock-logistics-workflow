# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
                }
            )
            move = cls.env["stock.move"].create(
                {
                    "picking_id": picking.id,
                    "name": "Test move 2",
                    "product_id": cls.product_2.id,
                    "product_uom": cls.product_2.uom_id.id,
                    "product_uom_qty": 5,
                    "location_id": cls.loc_stock.id,
                    "location_dest_id": cls.loc_customer.id,
                    "date": "2018-01-01 00:00:00",
                }
            )
            move._action_confirm()

            picking.action_assign()

            cls.pickings.append(picking)

    def test_one_single_loss_picking_for_same_quant(self):
        for picking in self.pickings:
            line = picking.move_line_ids
            line.qty_done = 1
            line.action_lose_quantity()
            quant_available_qty = self._get_quants_available_qty(line)
            self.assertEqual(
                quant_available_qty, 85
            )  # 100 (total) - 3*5 (from move lines)

        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(len(loss_picking.move_line_ids), 3)

    def test_loss_auto_clear(self):
        self.warehouse.loss_auto_clear_threshold = 3

        quant_available_qty_before = self._get_quants_available_qty(
            self.pickings[0].move_line_ids
        )
        for picking in self.pickings:
            line = picking.move_line_ids
            line.qty_done = 1
            line.action_lose_quantity()
        quant_available_qty_after = self._get_quants_available_qty(
            self.pickings[0].move_line_ids
        )

        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(len(loss_picking.move_line_ids), 4)
        last_loss_move_line = loss_picking.move_line_ids.sorted(lambda line: line.id)[
            -1
        ]
        self.assertEqual(
            last_loss_move_line.reserved_uom_qty, quant_available_qty_before
        )
        self.assertEqual(quant_available_qty_after, 0)
