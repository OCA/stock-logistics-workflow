# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestReservationBasedOnPlannedConsumedDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.product2 = cls.env.ref("product.product_product_13")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )

        cls.product.write({"tracking": "lot", "use_expiration_date": True})
        cls.product2.write({"tracking": "lot", "use_expiration_date": False})
        cls.lot1 = cls.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "expiration_date": "2024-01-25",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot2 = cls.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "expiration_date": "2024-02-02",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot_product2 = cls.env["stock.production.lot"].create(
            {
                "name": "lot product2",
                "product_id": cls.product2.id,
                "company_id": cls.warehouse.company_id.id,
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

    def _update_product_stock(self, qty, lot_id=False, location=None, product=None):
        if not product:
            product = self.product
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, product.ids)],
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
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                            "prod_lot_id": lot_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def test_procurement_without_expiration_date(self):
        self._update_product_stock(
            10,
            lot_id=self.lot_product2,
            product=self.product2,
            location=self.location_1,
        )
        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "one"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product2,
                    5,
                    self.product2.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict planned_consumed_date without lot",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "planned_consumed_date": "2024-01-15",
                    },
                ),
            ]
        )

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )

        pick = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(len(pick.move_ids_without_package), 1)

        self._assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package,
            self.lot_product2,
            self.location_1,
            datetime(2024, 1, 15),
            5,
        )

    def _assert_move_line_per_lot_and_location(
        self,
        moves,
        expect_lot,
        expect_from_location,
        expected_consumed_date,
        expect_reserved_qty,
    ):
        concern_move_line = moves.filtered(
            lambda mov: mov.lot_id == expect_lot
            and mov.location_id == expect_from_location
            and mov.move_id.planned_consumed_date == expected_consumed_date
        )
        self.assertEqual(len(concern_move_line), 1)
        self.assertEqual(concern_move_line.product_uom_qty, expect_reserved_qty)

    def test_procurement_with_2_steps_output(self):
        self._update_product_stock(10, lot_id=self.lot1, location=self.location_1)
        self._update_product_stock(10, lot_id=self.lot1, location=self.location_2)
        self._update_product_stock(5, lot_id=self.lot2, location=self.location_1)
        self._update_product_stock(25, lot_id=self.lot2, location=self.location_2)

        # create a procurement with two lines of same product with different lots
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

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        self.assertEqual(len(pickings), 2)
        pick = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(len(pick.move_ids_without_package), 2)

        self._assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package,
            self.lot1,
            self.location_1,
            datetime(2024, 1, 15),
            10,
        )
        self._assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package,
            self.lot1,
            self.location_2,
            datetime(2024, 1, 15),
            5,
        )
        self._assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package,
            self.lot2,
            self.location_1,
            datetime(2024, 1, 30),
            5,
        )
        self._assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package,
            self.lot2,
            self.location_2,
            datetime(2024, 1, 30),
            25,
        )
