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
        self.assertEqual(loss_picking.loss_declaration_count, 3)
        # 4 loss per picking = 3*4 = 12
        self.assertEqual(sum(loss_picking.move_ids.mapped("product_uom_qty")), 12)
        self.assertEqual(sum(loss_picking.move_ids.mapped("reserved_availability")), 12)

    def test_loss_auto_clear(self):
        self.warehouse.loss_auto_clear_threshold = 3

        for picking in self.pickings:
            line = picking.move_line_ids
            line.qty_done = 1
            line.action_lose_quantity()
        quant_available_qty_after = self._get_quants_available_qty(
            self.pickings[0].move_line_ids
        )

        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(loss_picking.loss_declaration_count, 3)
        # All quantity except done one = 100 - 3 = 97
        self.assertEqual(sum(loss_picking.move_ids.mapped("product_uom_qty")), 97)
        self.assertEqual(sum(loss_picking.move_ids.mapped("reserved_availability")), 97)
        self.assertEqual(quant_available_qty_after, 0)

    def test_auto_clear_parent_clears_child_location(self):
        self.warehouse.loss_auto_clear_threshold = 1
        loc_shelf = self.env["stock.location"].create(
            {"name": "Test Shelf", "location_id": self.loc_stock.id}
        )

        self._create_quantities(
            product=self.product_3, quantity=100.0, location=self.loc_stock
        )
        self._create_quantities(
            product=self.product_3, quantity=5.0, location=loc_shelf
        )

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test Move",
                            "product_id": self.product_3.id,
                            "product_uom_qty": 5,
                            "location_id": self.loc_stock.id,
                            "location_dest_id": self.loc_customer.id,
                        }
                    )
                ],
            }
        )
        picking.action_assign()

        line = picking.move_line_ids
        line.qty_done = 1
        line.action_lose_quantity()

        loss_picking = self._get_loss_pickings()
        self.assertEqual(len(loss_picking), 1)
        self.assertEqual(loss_picking.loss_declaration_count, 1)
        # All quantity except done one = 105 - 1 = 104
        self.assertEqual(sum(loss_picking.move_ids.mapped("product_uom_qty")), 104)
        self.assertEqual(
            sum(loss_picking.move_ids.mapped("reserved_availability")), 104
        )
