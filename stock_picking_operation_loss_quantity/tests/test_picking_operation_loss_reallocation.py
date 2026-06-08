# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import OperationLossQuantityCommon


class TestPickingOperationLossNewReservation(OperationLossQuantityCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shelf_a = cls.env["stock.location"].create(
            {
                "name": "Shelf A",
                "usage": "internal",
                "location_id": cls.loc_stock.id,
            }
        )
        cls.shelf_b = cls.env["stock.location"].create(
            {
                "name": "Shelf B",
                "usage": "internal",
                "location_id": cls.loc_stock.id,
            }
        )
        cls._create_quantities(cls.product_2, 5.0, location=cls.shelf_a)
        cls._create_quantities(cls.product_2, 2.0, location=cls.shelf_b)

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "name": "Test Fallback Move",
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 5,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move._action_confirm()
        cls.picking.action_assign()

    def test_loss_quantity_auto_reallocation(self):
        initial_line = self.move.move_line_ids[0]
        self.assertEqual(initial_line.location_id, self.shelf_a)
        fallback_location = self.shelf_b

        initial_line.action_lose_quantity()

        self.assertNotIn(initial_line, self.move.move_line_ids)

        self.assertEqual(len(self.move.move_line_ids), 1)
        new_line = self.move.move_line_ids[0]

        self.assertEqual(new_line.location_id, fallback_location)
        self.assertEqual(new_line.reserved_uom_qty, 2.0)

    def test_loss_quantity_partially_processed_move_auto_reallocation(self):
        # Increase demand to 7 to force reservation on both Shelf A (5) and Shelf B (2)
        self.move.product_uom_qty = 7.0
        self.picking.action_assign()

        self.assertEqual(len(self.move.move_line_ids), 2)
        line_shelf_a = self.move.move_line_ids.filtered(
            lambda l: l.location_id == self.shelf_a
        )
        line_shelf_b = self.move.move_line_ids.filtered(
            lambda l: l.location_id == self.shelf_b
        )
        self.assertEqual(line_shelf_a.reserved_uom_qty, 5.0)
        self.assertEqual(line_shelf_b.reserved_uom_qty, 2.0)

        # Put back enough qties to allow auto reallocation from shelf A
        self._create_quantities(self.product_2, 7.0, location=self.shelf_a)

        # Complete one and declare loss on the other
        line_shelf_a.qty_done = 5.0
        line_shelf_b.action_lose_quantity()

        # Only the processed line from Shelf A should remain
        self.assertNotIn(line_shelf_b, self.move.move_line_ids)
        self.assertEqual(len(self.move.move_line_ids), 1)
        remaining_line = self.move.move_line_ids[0]
        self.assertEqual(remaining_line.location_id, self.shelf_a)
        self.assertEqual(remaining_line.qty_done, 5.0)
        self.assertEqual(remaining_line.reserved_uom_qty, 7.0)

    def test_loss_quantity_auto_reallocation_same_location_different_lot(self):
        self.initiate_values()
        self.move_1.product_uom_qty = 3.0
        self.picking_1.action_assign()

        self.assertEqual(len(self.picking_1.move_line_ids), 1)
        inital_line = self.picking_1.move_line_ids
        self.assertEqual(inital_line.lot_id, self.product_1_lotA)

        inital_line.action_lose_quantity()

        self.assertEqual(len(self.picking_1.move_line_ids), 1)
        self.assertEqual(self.picking_1.move_line_ids.lot_id, self.product_1_lotB)
