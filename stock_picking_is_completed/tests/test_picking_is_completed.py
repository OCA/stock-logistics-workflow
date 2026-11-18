# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingIsReady(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product_model = cls.env["product.product"]
        cls.product_1 = cls.product_model.create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.product_2 = cls.product_model.create(
            {
                "name": "Product 2",
                "type": "product",
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "name": "Pick Test",
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "move_line_ids": [
                    Command.create(
                        {
                            "location_id": cls.suppliers_location.id,
                            "location_dest_id": cls.stock_location.id,
                            "product_id": cls.product_1.id,
                            "reserved_uom_qty": 2.0,
                            "product_uom_id": cls.product_1.uom_id.id,
                        }
                    ),
                    Command.create(
                        {
                            "location_id": cls.suppliers_location.id,
                            "location_dest_id": cls.stock_location.id,
                            "product_id": cls.product_2.id,
                            "reserved_uom_qty": 3.0,
                            "product_uom_id": cls.product_2.uom_id.id,
                        }
                    ),
                ],
            }
        )

    def test_picking_is_completed_move_lines(self):
        """
        Assign the picking
        Check that picking is not ready
        Fill in the quantity for the first movement
        Check that picking is not ready
        Fill in the quantity for the last movement
        Check that the picking is ready
        """
        self.picking.action_assign()
        self.assertFalse(self.picking.is_completed)
        # Fill in the first movement
        self.picking.move_line_ids[0].qty_done = 2.0
        self.assertFalse(self.picking.is_completed)

        # Fill in the second movement
        self.picking.move_line_ids[1].qty_done = 3.0
        self.assertTrue(self.picking.is_completed)

    def test_picking_is_completed_moves(self):
        """
        Assign the picking
        Check that picking is not ready
        Fill in the quantity for the first movement
        Check that picking is not ready
        Fill in the quantity for the last movement
        Check that the picking is ready
        """
        self.picking.action_assign()
        self.assertFalse(self.picking.is_completed)
        # Fill in the first movement
        self.picking.move_ids[0].quantity_done = 2.0
        self.assertFalse(self.picking.is_completed)

        # Fill in the second movement
        self.picking.move_ids[1].quantity_done = 3.0
        self.assertTrue(self.picking.is_completed)

    def test_picking_is_completed_search(self):
        """
        Assign the picking
        Check that picking is not ready
        Fill in the quantity for the first movement
        Check that picking is not ready
        Fill in the quantity for the last movement
        Check that the picking is ready
        """
        self.picking.action_assign()
        pickings = self.picking.search([("is_completed", "=", False)])
        self.assertIn(
            self.picking,
            pickings,
        )
        pickings = self.picking.search([("is_completed", "!=", True)])
        self.assertIn(
            self.picking,
            pickings,
        )
        self.assertFalse(self.picking.is_completed)
        # Fill in the first movement
        self.picking.move_ids[0].quantity_done = 2.0
        # Fill in the second movement
        self.picking.move_ids[1].quantity_done = 3.0
        pickings = self.picking.search([("is_completed", "=", True)])
        self.assertIn(
            self.picking,
            pickings,
        )
        pickings = self.picking.search([("is_completed", "!=", False)])
        self.assertIn(
            self.picking,
            pickings,
        )
