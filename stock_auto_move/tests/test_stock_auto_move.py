# Copyright 2014 NDP Systèmes (<https://www.ndp-systemes.fr>)
# Copyright 2020 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAutoMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_a1232 = cls.env.ref("product.product_product_6")
        cls.location_shelf = cls.env.ref("stock.stock_location_components")
        cls.location_1 = cls.env.ref("stock_auto_move.stock_location_a")
        cls.location_2 = cls.env.ref("stock_auto_move.stock_location_b")
        cls.location_3 = cls.env.ref("stock_auto_move.stock_location_c")
        cls.product_uom_unit_id = cls.env.ref("uom.product_uom_unit").id
        cls.picking_type_id = cls.env.ref("stock.picking_type_internal").id
        cls.auto_group_id = cls.env.ref("stock_auto_move.automatic_group").id
        cls.move_obj = cls.env["stock.move"]

    def test_10_auto_move(self):
        """Check automatic processing of move with auto_move set."""
        move = self.move_obj.create(
            {
                "name": "Test Auto",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 12,
                "location_id": self.location_1.id,
                "location_dest_id": self.location_2.id,
                "picking_type_id": self.picking_type_id,
                "auto_move": True,
            }
        )
        move2 = self.move_obj.create(
            {
                "name": "Test Manual",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 3,
                "location_id": self.location_1.id,
                "location_dest_id": self.location_2.id,
                "picking_type_id": self.picking_type_id,
                "auto_move": False,
            }
        )
        move._action_confirm()
        self.assertTrue(move.picking_id)
        self.assertEqual(move.group_id.id, self.auto_group_id)
        move2._action_confirm()
        self.assertTrue(move2.picking_id)
        self.assertFalse(move2.group_id)
        self.assertEqual(move.state, "confirmed")
        self.assertEqual(move2.state, "confirmed")
        move3 = self.move_obj.create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 25,
                "location_id": self.location_shelf.id,
                "location_dest_id": self.location_1.id,
                "auto_move": False,
            }
        )
        move3._action_confirm()
        move3._action_assign()
        move3.quantity_done = move3.product_qty
        move3._action_done()
        move._action_assign()
        move2._action_assign()
        self.assertEqual(move3.state, "done")
        self.assertEqual(move2.state, "assigned")
        self.assertEqual(move.state, "done")

    def test_20_procurement_auto_move(self):
        """Check that move generated with procurement rule
        have auto_move set."""
        self.product_a1232.route_ids = [(4, self.ref("stock_auto_move.test_route"))]
        moves_before = self.move_obj.search([])
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a1232,
                    1,
                    self.env.ref("uom.product_uom_unit"),
                    self.location_2,
                    "Test Procurement with auto_move",
                    "Test Procurement with auto_move",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": "2015-02-02 00:00:00",
                    },
                )
            ]
        )
        moves_after = self.move_obj.search([]) - moves_before
        self.assertEqual(
            moves_after.rule_id.id, self.ref("stock_auto_move.stock_rule_a_to_b"),
        )

        self.assertTrue(moves_after.auto_move)
        self.assertEqual(moves_after.state, "confirmed")

    def test_30_push_rule_auto(self):
        """Checks that push rule with auto set leads to an auto_move."""
        self.product_a1232.route_ids = [(4, self.ref("stock_auto_move.test_route"))]
        move3 = self.move_obj.create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 7,
                "location_id": self.location_shelf.id,
                "location_dest_id": self.location_3.id,
                "auto_move": False,
            }
        )
        move3._action_confirm()
        move3._auto_assign_quantities()
        move3._action_done()
        quants_in_3 = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_a1232.id),
                ("location_id", "=", self.location_3.id),
            ]
        )
        quants_in_1 = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_a1232.id),
                ("location_id", "=", self.location_1.id),
            ]
        )
        self.assertEqual(len(quants_in_3), 0)
        self.assertGreater(len(quants_in_1), 0)
