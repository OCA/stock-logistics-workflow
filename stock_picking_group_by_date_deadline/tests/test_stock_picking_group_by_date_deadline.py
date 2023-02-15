# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.tests.common import SavepointCase


class TestStockPickingGroupByDateDeadline(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        two_step_delivery_route = cls.env["stock.location.route"].search(
            [("name", "ilike", "deliver in 2")]
        )
        cls.product.categ_id.route_ids |= two_step_delivery_route

        cls.env["ir.config_parameter"].sudo().set_param(
            "stock_picking_group_by_date_deadline.deadline_date_rounding_threshold", 6
        )

    def test_create_stock_move_with_date_deadline(self):
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "date_deadline": datetime(2025, 6, 15, 11, 33),
            }
        )
        self.assertEqual(move.date_deadline, datetime(2025, 6, 15, 6, 0))

    def test_create_stock_move_without_date_deadline(self):
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "date_deadline": False,
            }
        )
        self.assertFalse(
            move.date_deadline,
        )

    def test_write_stock_move_with_date_deadline(self):
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
            }
        )
        move.write(
            {
                "date_deadline": datetime(2025, 6, 15, 11, 33),
            }
        )
        self.assertEqual(move.date_deadline, datetime(2025, 6, 15, 6, 0))

    def test_round_date_deadline(self):
        # TODO: could be nice to use parameterized here
        tested_values = [
            (24, datetime(2022, 12, 11, 12, 11, 5), datetime(2022, 12, 11, 0, 0, 0)),
            (0.5, datetime(2022, 12, 11, 13, 11, 5), datetime(2022, 12, 11, 13, 0, 0)),
            (6, datetime(2022, 12, 11, 12, 11, 5), datetime(2022, 12, 11, 12, 0, 0)),
            (0.5, False, False),
        ]

        for round_hours, dt, expected_dt in tested_values:
            self.env["ir.config_parameter"].sudo().set_param(
                "stock_picking_group_by_date_deadline.deadline_date_rounding_threshold",
                round_hours,
            )
            res = self.env["stock.move"]._round_date_deadline(dt)
            self.assertEqual(
                expected_dt,
                res,
                (
                    f"Rounding by {round_hours} hours current date "
                    f"{dt} expected {expected_dt} != received {res}"
                ),
            )

    def _update_product_stock(self, qty, location=None):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, self.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": qty,
                            "location_id": location.id
                            if location
                            else self.warehouse.lot_stock_id.id,
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def _run_procurement(self, qty_per_deadline):
        """qty_per_deadline is a list of tuple with deadline date, qty::

        [(5, datetime(2022, 2, 1, 11, 22)), (10, datetime(2022, 2, 10, 8, 5))]
        """
        self._update_product_stock(sum([qty for _, qty in qty_per_deadline]))

        # create a procurement with two lines of same product
        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "one"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    qty,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin with ",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "date_deadline": deadline_date,
                    },
                )
                for deadline_date, qty in qty_per_deadline
            ]
        )
        return procurement_group

    def assert_move_qty_per_deadline_date(
        self, moves, expect_deadline_date, expect_qty
    ):
        concern_move = moves.filtered(
            lambda mov: mov.date_deadline == expect_deadline_date
        )
        self.assertEqual(len(concern_move), 1)
        self.assertEqual(concern_move.product_uom_qty, expect_qty)
        self.assertEqual(
            concern_move.date_deadline, concern_move.picking_id.date_deadline
        )

    def test_procurement_with_2_steps_output_with_different_datetime(self):

        date1 = datetime(2123, 2, 12, 16, 25, 32)
        expected_delivery1_deadline = datetime(2123, 2, 12, 12, 0, 0)
        date2 = datetime(2123, 2, 12, 19, 25, 32)
        expected_delivery2_deadline = datetime(2123, 2, 12, 18, 0, 0)
        procurement_group = self._run_procurement(
            [
                (date1, 11),
                (date2, 22),
            ]
        )

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        self.assertEqual(len(pickings.move_ids_without_package), 4)
        self.assertEqual(len(pickings), 4)
        deliveries = pickings.filtered(
            lambda pick: pick.picking_type_id.code == "outgoing"
        )
        picks = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        self.assert_move_qty_per_deadline_date(
            deliveries.move_ids_without_package, expected_delivery1_deadline, 11
        )
        self.assert_move_qty_per_deadline_date(
            deliveries.move_ids_without_package, expected_delivery2_deadline, 22
        )

        self.assert_move_qty_per_deadline_date(
            picks.move_ids_without_package, expected_delivery1_deadline, 11
        )
        self.assert_move_qty_per_deadline_date(
            picks.move_ids_without_package, expected_delivery2_deadline, 22
        )

    def test_procurement_with_2_steps_output_with_same_datetime(self):

        date1 = datetime(2123, 2, 12, 16, 25, 32)
        expected_delivery1_deadline = datetime(2123, 2, 12, 12, 0, 0)
        date2 = datetime(2123, 2, 12, 14, 33, 22)
        expected_delivery2_deadline = datetime(2123, 2, 12, 12, 0, 0)
        procurement_group = self._run_procurement(
            [
                (date1, 11),
                (date2, 22),
            ]
        )

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        self.assertEqual(len(pickings.move_ids_without_package), 2)
        self.assertEqual(len(pickings), 2)
        deliveries = pickings.filtered(
            lambda pick: pick.picking_type_id.code == "outgoing"
        )
        picks = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        self.assert_move_qty_per_deadline_date(
            deliveries.move_ids_without_package, expected_delivery1_deadline, 33
        )

        self.assert_move_qty_per_deadline_date(
            picks.move_ids_without_package, expected_delivery2_deadline, 33
        )
