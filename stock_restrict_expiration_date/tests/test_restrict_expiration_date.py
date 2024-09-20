# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo.tests.common import SavepointCase


class TestReservationBasedOnPlannedConsumedDate(SavepointCase):
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

        cls.product.write({"tracking": "lot", "use_expiration_date": True})

        cls.lot1 = cls.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "expiration_date": "2024-01-25 15:15",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot2 = cls.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "expiration_date": "2024-02-02 16:16",
                "product_id": cls.product.id,
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

    def _update_product_stock(self, qty, lot_id=False, location=None):
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
                            "prod_lot_id": lot_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def assert_move_line_per_lot_and_location(
        self,
        move_lines,
        expect_lot=None,
        expect_from_location=None,
        expect_restrict_expiration_date=None,
        expect_reserved_qty=0,
    ):
        concern_move_line = move_lines.filtered(
            lambda mov: (expect_lot is None or mov.lot_id == expect_lot)
            and (
                expect_from_location is None or mov.location_id == expect_from_location
            )
            and (
                expect_restrict_expiration_date is None
                or mov.move_id.restrict_expiration_date
                == expect_restrict_expiration_date
            )
        )
        self.assertEqual(
            len(concern_move_line),
            1,
            "Expect only one stock.move.line found matching lot: "
            f"{expect_lot.name if expect_lot is not None else expect_lot}, "
            f"location: {expect_from_location if expect_lot is not None else expect_lot}, "
            f"restrict expiration date {expect_restrict_expiration_date}. "
            "None accept all values",
        )
        self.assertEqual(concern_move_line.product_uom_qty, expect_reserved_qty)

    def test_procurement_with_2_steps_output(self):
        self._update_product_stock(10, lot_id=self.lot1, location=self.location_1)
        self._update_product_stock(10, lot_id=self.lot1, location=self.location_2)
        self._update_product_stock(5, lot_id=self.lot2, location=self.location_1)
        self._update_product_stock(25, lot_id=self.lot2, location=self.location_2)

        # create a procurement with two lines of same product with different lots
        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "direct"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    15,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "Restrict expiration date lot 1",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_expiration_date": "2024-01-25",
                    },
                ),
                self.env["procurement.group"].Procurement(
                    self.product,
                    30,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "Restrict with expiration date lot 2",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_expiration_date": "2024-02-02",
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
        self.assertEqual(len(pick.move_lines), 2)

        self.assert_move_line_per_lot_and_location(
            pick.move_line_ids,
            expect_lot=self.lot1,
            expect_from_location=self.location_1,
            expect_restrict_expiration_date=date(2024, 1, 25),
            expect_reserved_qty=10,
        )
        self.assert_move_line_per_lot_and_location(
            pick.move_line_ids,
            expect_lot=self.lot1,
            expect_from_location=self.location_2,
            expect_restrict_expiration_date=date(2024, 1, 25),
            expect_reserved_qty=5,
        )
        self.assert_move_line_per_lot_and_location(
            pick.move_line_ids,
            expect_lot=self.lot2,
            expect_from_location=self.location_1,
            expect_restrict_expiration_date=date(2024, 2, 2),
            expect_reserved_qty=5,
        )
        self.assert_move_line_per_lot_and_location(
            pick.move_line_ids,
            expect_lot=self.lot2,
            expect_from_location=self.location_2,
            expect_restrict_expiration_date=date(2024, 2, 2),
            expect_reserved_qty=25,
        )

    def test_procurement_with_no_lot_matching_restrict_expiration_date(self):
        self._update_product_stock(10, lot_id=self.lot1, location=self.location_1)

        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "direct"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    5,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "Restrict expiration date not lot match",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_expiration_date": "2024-02-02",
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
        self.assertEqual(pick.state, "confirmed")
        self.assertEqual(len(pick.move_line_ids), 0)

        self._update_product_stock(10, lot_id=self.lot2, location=self.location_1)
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(len(pick.move_lines), 1)

        self.assert_move_line_per_lot_and_location(
            pick.move_line_ids,
            expect_lot=self.lot2,
            expect_from_location=self.location_1,
            expect_restrict_expiration_date=date(2024, 2, 2),
            expect_reserved_qty=5,
        )
