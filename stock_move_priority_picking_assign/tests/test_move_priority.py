# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestStockMovePriority(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "product",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.env.company.stock_move_manage_priority = True

    @classmethod
    def _create_procurement(cls, qty, priority, multi=False):
        procurements = [
            cls.env["procurement.group"].Procurement(
                cls.product,
                qty,
                cls.product.uom_id,
                cls.customers,
                cls.product.name,
                "",
                cls.env.company,
                {
                    "priority": priority,
                    "partner_id": cls.partner.id,
                },
            )
        ]
        if multi:
            # Product 2 is always with priority == "0"
            procurements.append(
                cls.env["procurement.group"].Procurement(
                    cls.product_2,
                    qty,
                    cls.product.uom_id,
                    cls.customers,
                    cls.product_2.name,
                    "",
                    cls.env.company,
                    {
                        "priority": "0",
                        "partner_id": cls.partner.id,
                    },
                )
            )
        cls.env["procurement.group"].run(procurements)

    def test_move_priority(self):
        """
        Check if the priority set on the stock move is transmitted
        to the picking.
        """
        # Cancel existing pickings
        pickings = self.env["stock.picking"].search(
            [("state", "not in", ("done", "cancel"))]
        )
        pickings.action_cancel()
        self.product.route_ids |= self.warehouse.delivery_route_id
        self._create_procurement(10, "1")
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertTrue(move.picking_id)
        self.assertEqual("1", move.picking_id.priority)

    def test_move_priority_multi(self):
        """
        Check if the max priority set on the stock move is transmitted
        to the picking.

        Both moves are in the same picking
        """
        # Cancel existing pickings
        pickings = self.env["stock.picking"].search(
            [("state", "not in", ("done", "cancel"))]
        )
        pickings.action_cancel()
        self.product.route_ids |= self.warehouse.delivery_route_id
        self.product_2.route_ids |= self.warehouse.delivery_route_id
        self._create_procurement(10, "1", multi=True)
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertTrue(move.picking_id)
        self.assertEqual("1", move.picking_id.priority)
        move_2 = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertEqual(move.picking_id, move_2.picking_id)
        self.assertEqual(move_2.priority, "0")

    def test_move_priority_multi_grouped(self):
        """
        Check if the max priority set on the stock move is transmitted
        to the picking.

        Both moves are in the different picking
        """
        # Activate the grouping option
        self.warehouse.out_type_id.group_moves_per_priority = True
        # Cancel existing pickings
        pickings = self.env["stock.picking"].search(
            [("state", "not in", ("done", "cancel"))]
        )
        pickings.action_cancel()
        self.product.route_ids |= self.warehouse.delivery_route_id
        self.product_2.route_ids |= self.warehouse.delivery_route_id
        self._create_procurement(10, "1", multi=True)
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertTrue(move.picking_id)
        self.assertEqual("1", move.picking_id.priority)
        move_2 = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertNotEqual(move.picking_id, move_2.picking_id)
