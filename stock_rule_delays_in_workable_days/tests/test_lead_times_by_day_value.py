# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import ValidationError

from .common import CommonStockPurchaseOrderDateRule


class TestLeadByDayValue(CommonStockPurchaseOrderDateRule):
    def test_check_value(self):
        with self.assertRaises(ValidationError):
            self.env["lead_times_by_day.value"].create({"value": -1})

    def test_name_get(self):
        self.assertEqual(
            self.lead_times_by_day_value_2.name_get(),
            [(self.lead_times_by_day_value_2.id, "2 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_10.name_get(),
            [(self.lead_times_by_day_value_10.id, "10 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_11.name_get(),
            [(self.lead_times_by_day_value_11.id, "11 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_12.name_get(),
            [(self.lead_times_by_day_value_12.id, "12 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_14.name_get(),
            [(self.lead_times_by_day_value_14.id, "14 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_15.name_get(),
            [(self.lead_times_by_day_value_15.id, "15 day(s)")],
        )
        self.assertEqual(
            self.lead_times_by_day_value_16.name_get(),
            [(self.lead_times_by_day_value_16.id, "16 day(s)")],
        )

    def test_name_search_1(self):
        results = [
            record[0] for record in self.env["lead_times_by_day.value"].name_search("1")
        ]
        self.assertIn(self.lead_times_by_day_value_12.id, results)
        self.assertIn(self.lead_times_by_day_value_10.id, results)
        self.assertIn(self.lead_times_by_day_value_11.id, results)
        self.assertIn(self.lead_times_by_day_value_14.id, results)
        self.assertIn(self.lead_times_by_day_value_15.id, results)
        self.assertIn(self.lead_times_by_day_value_16.id, results)
        self.assertNotIn(self.lead_times_by_day_value_2.id, results)

    def test_name_search_2(self):
        results = [
            record[0] for record in self.env["lead_times_by_day.value"].name_search("2")
        ]
        self.assertIn(self.lead_times_by_day_value_2.id, results)
        self.assertIn(self.lead_times_by_day_value_12.id, results)
        self.assertNotIn(self.lead_times_by_day_value_10.id, results)
        self.assertNotIn(self.lead_times_by_day_value_11.id, results)
        self.assertNotIn(self.lead_times_by_day_value_14.id, results)
        self.assertNotIn(self.lead_times_by_day_value_15.id, results)
        self.assertNotIn(self.lead_times_by_day_value_16.id, results)

    def test_get_or_create_1(self):
        self.assertEqual(
            self.lead_times_by_day_value_2,
            self.env["lead_times_by_day.value"].get_or_create_by_value(2),
        )

    def test_get_or_create_2(self):
        self.assertEqual(
            0, len(self.env["lead_times_by_day.value"].search([("value", "=", 1)]))
        )
        lead_times_by_day_value_1 = self.env[
            "lead_times_by_day.value"
        ].get_or_create_by_value(1)
        self.assertEqual(
            1,
            lead_times_by_day_value_1.value,
        )
        self.assertEqual(
            lead_times_by_day_value_1,
            self.env["lead_times_by_day.value"].search([("value", "=", 1)]),
        )
