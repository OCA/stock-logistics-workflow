# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockLotRemove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.loc_stock_child_1 = cls.env["stock.location"].create(
            {
                "name": "Child Location 1",
                "location_id": cls.loc_stock.id,
                "usage": "internal",
            }
        )
        cls.loc_stock_child_2 = cls.env["stock.location"].create(
            {
                "name": "Child Location 2",
                "location_id": cls.loc_stock.id,
                "usage": "internal",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "tracking": "lot",
                "type": "product",
                "use_expiration_date": True,
            }
        )
        cls.lot_2023 = cls.env["stock.lot"].create(
            {
                "name": "lot",
                "product_id": cls.product.id,
                "expiration_date": "2023-01-31",
            }
        )
        cls.lot_2024 = cls.env["stock.lot"].create(
            {
                "name": "lot2",
                "product_id": cls.product.id,
                "expiration_date": "2024-01-31",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock_child_1, 3, lot_id=cls.lot_2023
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock_child_2, 6, lot_id=cls.lot_2024
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.warehouse.lot_remove_orig_location_ids = cls.loc_stock

        cls.quant_2013 = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.product.id),
                ("lot_id", "=", cls.lot_2023.id),
                ("location_id", "=", cls.loc_stock_child_1.id),
            ],
            limit=1,
        )
        cls.quant_2014 = cls.env["stock.quant"].search(
            [
                ("product_id", "=", cls.product.id),
                ("lot_id", "=", cls.lot_2024.id),
                ("location_id", "=", cls.loc_stock_child_2.id),
            ],
            limit=1,
        )

    @classmethod
    def _create_and_assign_picking(cls):
        """Create a picking with the product and lots.
        Picking will consume:
        * 3 from lot 2013
        * 2 from lot 2014
        """
        picking_out = cls.env["stock.picking"].create(
            {
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.customer_location.id,
                            "warehouse_id": cls.warehouse.id,
                        }
                    )
                ],
            }
        )
        picking_out.action_confirm()
        picking_out.action_assign()
        return picking_out

    @classmethod
    def _create_and_assign_multi_pickings(cls):
        """Create two pickings with the same product and lots.
        * picking 1 consume:
            * 3 from lot 2013
            * 2 from lot 2014
        * picking 2 consume:
            * 1 from lot 2014
        """
        picking_out = cls._create_and_assign_picking()
        picking_out2 = cls.env["stock.picking"].create(
            {
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.customer_location.id,
                            "warehouse_id": cls.warehouse.id,
                        }
                    )
                ],
            }
        )
        picking_out2.action_confirm()
        picking_out2.action_assign()
        return picking_out, picking_out2

    def _assert_initial_situation(self, picking):
        """Assert the initial situation of the stock."""
        self.assertEqual(
            len(self.quant_2013),
            1,
        )
        self.assertEqual(
            len(self.quant_2014),
            1,
        )
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(len(picking.move_line_ids), 2)
        self.assertRecordValues(
            picking.move_line_ids,
            [
                {
                    "lot_id": self.lot_2023.id,
                    "reserved_uom_qty": 3,
                    "qty_done": 0,
                },
                {
                    "lot_id": self.lot_2024.id,
                    "reserved_uom_qty": 2,
                    "qty_done": 0,
                },
            ],
        )
        lot_ids = picking.move_line_ids.lot_id
        self.assertEqual(lot_ids, self.lot_2023 | self.lot_2024)

    @freeze_time("2022-01-01")
    def test_remove_nothing(self):
        """Test that no expired lot is removed when there are no expired lots."""
        picking_out = self._create_and_assign_picking()
        self._assert_initial_situation(picking_out)
        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
                "removal_date": "2022-01-01",
            }
        )
        picking = wizard.action_run()
        self.assertFalse(picking)
        self._assert_initial_situation(picking_out)

    @freeze_time("2024-01-01")
    def test_remove_expired_lots(self):
        """Test that expired lots are removed if the process is not started."""
        picking_out = self._create_and_assign_picking()
        self._assert_initial_situation(picking_out)

        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)
        self.assertEqual(len(picking_remove.move_ids), 1)
        self.assertEqual(len(picking_remove.move_line_ids), 1)

        # at this stage, the lot 2013 should be assigned to be removed
        self.assertEqual(
            picking_remove.move_line_ids.lot_id,
            self.lot_2023,
        )
        self.assertEqual(
            picking_remove.move_line_ids.reserved_uom_qty,
            3,
        )

        # the original picking should have been updated to not include the lot 2013
        self.assertEqual(
            picking_out.move_line_ids.lot_id,
            self.lot_2024,
        )

        # since we have enough quantity in the lot 2014 to cover the initial picking,
        # the original picking should be fully assigned
        self.assertEqual(
            picking_out.move_line_ids.reserved_uom_qty,
            5,
        )

    @freeze_time("2024-01-01")
    def test_remove_expired_lots_no_remove_wip(self):
        """Test that expired lots are partially removed if a move line is partially done."""
        picking_out = self._create_and_assign_picking()
        self._assert_initial_situation(picking_out)

        lot_2013_line = picking_out.move_line_ids.filtered(
            lambda ml: ml.lot_id == self.lot_2023
        )
        lot_2013_line.qty_done = 1  # Simulate that part of the

        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)

        # The line for the lot 2013 into the first picking should be preserved
        # with 1 quantity done but only 1 reserved_uom_qty
        self.assertRecordValues(
            picking_out.move_line_ids,
            [
                {
                    "lot_id": self.lot_2023.id,
                    "reserved_uom_qty": 1,
                    "qty_done": 1,
                },
                {
                    "lot_id": self.lot_2024.id,
                    "reserved_uom_qty": 4,
                    "qty_done": 0,
                },
            ],
        )

    @freeze_time("2025-01-01")
    def test_remove_expired_lots_in_multiple_pickings(self):
        """Test that expired lots are removed in multiple pickings."""
        picking_out, picking_out2 = self._create_and_assign_multi_pickings()
        self._assert_initial_situation(picking_out)
        self.assertEqual(
            picking_out2.move_line_ids.reserved_uom_qty,
            1,
        )
        self.assertEqual(
            picking_out2.move_line_ids.lot_id,
            self.lot_2024,
        )

        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)
        self.assertEqual(len(picking_remove.move_ids), 2)
        self.assertEqual(len(picking_remove.move_line_ids), 2)
        self.assertEqual(
            picking_remove.move_line_ids.lot_id, self.lot_2023 | self.lot_2024
        )
        self.assertEqual(
            sum(picking_remove.move_line_ids.mapped("reserved_uom_qty")), 9
        )

    @freeze_time("2025-01-01")
    def test_remove_expired_lots_in_multiple_pickings_no_remove_wip(self):
        """Test that expired lots are partially removed a move line is partially done."""
        picking_out, picking_out2 = self._create_and_assign_multi_pickings()
        lot_2014_line = picking_out.move_line_ids.filtered(
            lambda ml: ml.lot_id == self.lot_2024
        )
        lot_2014_line.qty_done = 1
        # We simulate that part of the lot 2014 is done in the first picking
        # but not into the second one. Therefore, the lot 2014 should be
        # partially removed for the remaining quantity
        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)
        # The line for the lot 2014 into the first picking should be preserved
        # with 1 quantity done but only 1 reserved_uom_qty
        lot_2014_line = picking_out.move_line_ids.filtered(
            lambda ml: ml.lot_id == self.lot_2024
        )
        self.assertEqual(lot_2014_line.qty_done, 1)
        self.assertEqual(lot_2014_line.reserved_uom_qty, 1)

        # in the picking_out1, we must only have one live for the lot 2014
        self.assertEqual(len(picking_out.move_line_ids), 1)
        self.assertRecordValues(
            picking_out.move_line_ids,
            [
                {
                    "lot_id": self.lot_2024.id,
                    "reserved_uom_qty": 1,
                    "qty_done": 1,
                }
            ],
        )
        self.assertRecordValues(
            picking_out.move_ids,
            [
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 5,
                }
            ],
        )

        # since no more quantity are available picking_out2 must be confirmed
        self.assertEqual(picking_out2.state, "confirmed")
        self.assertRecordValues(
            picking_out2.move_ids,
            [
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1,
                    "move_line_ids": self.env["stock.move.line"],
                }
            ],
        )

        # in out removal picking, we must have two lines:
        # - one for the lot 2013 with 3 reserved_uom_qty
        # - one for the lot 2014 with 5 reserved_uom_qty
        self.assertRecordValues(
            picking_remove.move_line_ids,
            [
                {
                    "lot_id": self.lot_2023.id,
                    "reserved_uom_qty": 3,
                },
                {
                    "lot_id": self.lot_2024.id,
                    "reserved_uom_qty": 5,
                },
            ],
        )

        # the expired quants should be fully reserved
        self.assertEqual(self.quant_2013.reserved_quantity, 3)
        self.assertEqual(self.quant_2014.reserved_quantity, 6)

    def test_remove_expired_lots_remove_once(self):
        """Test that expired lots are removed only once."""
        with freeze_time("2024-01-01"):
            picking_out = self._create_and_assign_picking()
            self._assert_initial_situation(picking_out)

            wizard = self.env["stock.lot.removal.wizard"].create(
                {
                    "warehouse_id": self.warehouse.id,
                }
            )
            picking_remove = wizard.action_run()
            self.assertTrue(picking_remove)
            self.assertEqual(self.quant_2013.reserved_quantity, 3)

        with freeze_time("2024-01-02"):
            wizard = self.env["stock.lot.removal.wizard"].create(
                {
                    "warehouse_id": self.warehouse.id,
                }
            )
            picking_remove = wizard.action_run()
            self.assertFalse(picking_remove)
            self.assertEqual(self.quant_2013.reserved_quantity, 3)

    @freeze_time("2026-01-01")
    def test_remove_expired_lots_multi_src_locations(self):
        """Test that expired lots are removed with multiple source locations."""
        loc_stock_child_3 = self.env["stock.location"].create(
            {
                "name": "Child Location 3",
                "location_id": self.loc_stock.id,
                "usage": "internal",
            }
        )
        lot_2024_bis = self.env["stock.lot"].create(
            {
                "name": "lot3",
                "product_id": self.product.id,
                "expiration_date": "2024-01-31",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, loc_stock_child_3, 20, lot_id=lot_2024_bis
        )
        self.warehouse.lot_remove_orig_location_ids = (
            self.loc_stock_child_1 | self.loc_stock_child_2
        )

        picking_out = self._create_and_assign_picking()
        self._assert_initial_situation(picking_out)

        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)
        self.assertEqual(
            picking_remove.move_line_ids.lot_id, self.lot_2023 | self.lot_2024
        )

        self.warehouse.lot_remove_orig_location_ids = (
            self.loc_stock_child_1 | self.loc_stock_child_2 | loc_stock_child_3
        )
        wizard = self.env["stock.lot.removal.wizard"].create(
            {
                "warehouse_id": self.warehouse.id,
            }
        )
        picking_remove = wizard.action_run()
        self.assertTrue(picking_remove)
        self.assertEqual(picking_remove.move_line_ids.lot_id, lot_2024_bis)
