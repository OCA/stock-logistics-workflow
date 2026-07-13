# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingPutawayRecomputeCron(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product_1 = cls.env.ref("product.product_product_4")
        cls.product_2 = cls.env.ref("product.product_product_5")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.warehouse = cls.env.ref("stock.warehouse0")

        cls.product_1.weight = 1.0
        cls.product_2.weight = 1.0

        # --- Storage Category with Max Weight ---
        cls.storage_category = cls.env["stock.storage.category"].create(
            {
                "name": "Max 10kg Category",
                "max_weight": 1.0,
                "company_id": cls.env.company.id,
            }
        )

        cls.main_loc = cls.env["stock.location"].create(
            {
                "name": "Main Receiving Area",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.sub_loc = cls.env["stock.location"].create(
            {
                "name": "Preferred Shelf 1",
                "usage": "internal",
                "location_id": cls.main_loc.id,
                "storage_category_id": cls.storage_category.id,
            }
        )

        cls.env["stock.putaway.rule"].create(
            [
                {
                    "location_in_id": cls.main_loc.id,
                    "location_out_id": cls.sub_loc.id,
                    "product_id": product.id,
                }
                for product in [cls.product_1, cls.product_2]
            ]
        )

        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Internal Transfer Putaway",
                "sequence_code": "INT",
                "warehouse_id": cls.warehouse.id,
                "code": "internal",
                "default_location_src_id": cls.stock_loc.id,
                "default_location_dest_id": cls.main_loc.id,
                "allow_to_recompute_putaways": True,
            }
        )

        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_loc, 1.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.stock_loc, 1.0
        )

    def test_putaway_recompute_on_freed_location(self):
        """
        Tests that Move B is reassigned to the optimal sub-location
        after Move A clears the 'blockage' and the cron runs.
        """
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.main_loc.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Move A",
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.stock_loc.id,
                            "location_dest_id": self.main_loc.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Move B",
                            "product_id": self.product_2.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.stock_loc.id,
                            "location_dest_id": self.main_loc.id,
                        }
                    ),
                ],
            }
        )

        picking.action_assign()

        move_a = picking.move_ids.filtered(lambda m: m.name == "Move A")
        move_b = picking.move_ids.filtered(lambda m: m.name == "Move B")

        self.assertEqual(move_a.state, "assigned")
        ml_a = move_a.move_line_ids
        self.assertEqual(ml_a.location_dest_id, self.sub_loc)

        ml_b = move_b.move_line_ids
        self.assertEqual(ml_b.location_dest_id, self.main_loc)

        # ↓ This will free sub_loc
        move_a._action_cancel()

        self.env["stock.move.line"].cron_auto_recompute_putaways()
        self.assertEqual(ml_b.location_dest_id, self.sub_loc)

    def test_filter_no_picking_move_lines(self):
        """
        Ensures that move lines not linked to any picking are filtered
        out from the putaway recomputation (such move lines cause an error)
        """
        StockMoveLine = self.env["stock.move.line"]

        invalid_move_line = StockMoveLine.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.product_1.uom_id.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.main_loc.id,
                "qty_done": 0,
                "company_id": self.env.company.id,
            }
        )
        self.assertFalse(invalid_move_line.picking_id)

        move_lines_for_putaway = StockMoveLine.search(
            StockMoveLine._get_putaway_recompute_domain()
        )
        self.assertNotIn(invalid_move_line, move_lines_for_putaway)
