# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tests.common import SavepointCase


class TestPropagatePlannedConsumedDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )

        cls.product.categ_id.route_ids |= cls.env["stock.location.route"].search(
            [("name", "ilike", "deliver in 2")]
        )
        cls.location_1 = cls.env["stock.location"].create(
            {"name": "loc1", "location_id": cls.warehouse.lot_stock_id.id}
        )
        cls.location_2 = cls.env["stock.location"].create(
            {"name": "loc2", "location_id": cls.warehouse.lot_stock_id.id}
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

    def test_procurement_with_2_steps_output(self):

        self._update_product_stock(10, location=self.location_1)
        self._update_product_stock(10, location=self.location_2)
        self._update_product_stock(5, location=self.location_1)
        self._update_product_stock(25, location=self.location_2)

        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "one"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    15,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict planned_consumed_date 1",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "planned_consumed_date": "2024-01-15",
                    },
                ),
                self.env["procurement.group"].Procurement(
                    self.product,
                    30,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict planned_consumed_date 2",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "planned_consumed_date": "2024-01-30",
                    },
                ),
            ]
        )

        def assert_move_qty_per_planned_consumed_date(moves, expect_date, expect_qty):
            concern_move = moves.filtered(
                lambda mov: mov.planned_consumed_date == expect_date
            )
            self.assertEqual(len(concern_move), 1)
            self.assertEqual(concern_move.product_uom_qty, expect_qty)

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        self.assertEqual(len(pickings), 2)
        delivery = pickings.filtered(
            lambda pick: pick.picking_type_id.code == "outgoing"
        )
        pick = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        self.assertEqual(delivery.state, "waiting")
        self.assertEqual(len(delivery.move_ids_without_package), 2)
        assert_move_qty_per_planned_consumed_date(
            delivery.move_ids_without_package, datetime(2024, 1, 15), 15
        )
        assert_move_qty_per_planned_consumed_date(
            delivery.move_ids_without_package, datetime(2024, 1, 30), 30
        )

        self.assertEqual(pick.state, "confirmed")
        self.assertEqual(len(delivery.move_ids_without_package), 2)
        assert_move_qty_per_planned_consumed_date(
            pick.move_ids_without_package, datetime(2024, 1, 15), 15
        )
        assert_move_qty_per_planned_consumed_date(
            pick.move_ids_without_package, datetime(2024, 1, 30), 30
        )
