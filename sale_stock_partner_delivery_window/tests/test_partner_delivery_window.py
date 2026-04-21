# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command, fields
from odoo.tests import Form

from odoo.addons.stock_partner_delivery_window.tests.common import (
    PartnerDeliveryWindowCommon,
)


class TestSalePartnerDeliveryWindow(PartnerDeliveryWindowCommon):
    @classmethod
    def _create_order(cls, partner):
        return cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": cls.product.id, "product_uom_qty": 1}
                    ),
                ],
            }
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_anytime(self):
        """Customer with no delivery preferences.

        Expected date = order creation time (no delays).
        """
        order = self._create_order(self.customer_anytime)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-02 10:00:00",
            "The same day is fine",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_anytime_with_sale_delay(self):
        """Customer with no preferences + product sale delay.

        Expected date = order date + sale_delay (2 days: Thu → Sat).
        """
        self.product.sale_delay = 2
        order = self._create_order(self.customer_anytime)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-04 10:00:00",
            "2 days after, because of the sale delay",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_working_days_ok(self):
        """Working-days-only customer, order on weekday (Thursday).

        Expected date = same day (already a valid working day).
        """
        order = self._create_order(self.customer_working_days)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-02 10:00:00",
            "The same day is fine",
        )

    @freeze_time("2020-04-04 10:00:00")  # Saturday
    def test_expected_date_working_days_on_saturday(self):
        """Working-days-only customer, order on Saturday.

        Expected date = next Monday (first available working day).
        """
        order = self._create_order(self.customer_working_days)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-06 10:00:00",
            "Next Monday is the first available working day",
        )

    @freeze_time("2020-04-05 10:00:00")  # Sunday
    def test_expected_date_working_days_on_sunday(self):
        """Working-days-only customer, order on Sunday.

        Expected date = next Monday (first available working day).
        """
        order = self._create_order(self.customer_working_days)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-06 10:00:00",
            "Next Monday is the first available working day",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_working_days_with_sale_delay(self):
        """Working-days-only customer + sale delay.

        • Order on Thursday, sale_delay = 2 days (Thursday → Saturday)
        • Expected date = next Monday (first available working day)
        """
        self.product.sale_delay = 2
        order = self._create_order(self.customer_working_days)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-06 10:00:00",
            "Next Monday is the first available working day, after the sale delay",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_time_windows_same_day(self):
        """Time-window customer, order on valid delivery day (Thursday).

        Expected date = same day at current time.
        """
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-02 10:00:00",
            "The same day is fine",
        )

    @freeze_time("2020-04-03 10:00:00")  # Friday
    def test_expected_date_time_windows_next_available_day(self):
        """Time-window customer, order on invalid day (Friday).

        • Delivery windows: Thursdays and Saturdays
        • Expected date = next Saturday at 00:00
        """
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-04 00:00:00",
            "Saturday is the next available day (Thursdays and Saturdays deliveries)",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_time_windows_next_available_time(self):
        """Time-window customer, order before delivery window (10am, window 2pm-6pm).

        Expected date = same day at window start (2pm), not next day.
        """
        # The current day is ok, but not the time slot
        # Expected date must be delayed just for a few hours
        self.customer_time_window.delivery_time_window_ids.write(
            {"time_window_start": 14.0, "time_window_end": 18.0}
        )
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-02 14:00:00",
            "The next available time slot is 2pm to 6pm",
        )

    @freeze_time("2020-04-02 20:00:00")  # Thursday
    def test_expected_date_time_windows_no_available_time(self):
        """Time-window customer, order after delivery window (8pm, window 2pm-6pm).

        Expected date = next delivery day (Saturday) at window start (2pm).
        """
        # The current day is ok, but not the time slot
        # However, the slots have already passed for the day
        self.customer_time_window.delivery_time_window_ids.write(
            {"time_window_start": 14.0, "time_window_end": 18.0}
        )
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-04 14:00:00",
            "The next available day is Saturday from 2pm to 6pm",
        )

    @freeze_time("2020-04-06 19:00:00")  # Monday
    def test_expected_date_time_windows_no_available_time_until_next_week(self):
        """Time-window customer, order in one week (Monday).

        Expected date = next Monday at window start (2pm).
        """
        # The current day is ok, but not the time slot
        # However, the slots have already passed for the day
        # Whilst delivery is only possible on Mondays
        self.customer_time_window.delivery_time_window_ids.write(
            {
                "time_window_start": 14.0,
                "time_window_end": 18.0,
                "time_window_weekday_ids": [
                    Command.set(
                        self.env.ref("base_time_window.time_weekday_monday").ids
                    )
                ],
            }
        )
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-13 14:00:00",
            "The next available day is Monday from 2pm to 6pm",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_expected_date_time_windows_with_sale_delay(self):
        """Time-window customer + sale delay.

        • Order on Thursday, sale_delay = 3 days (Thursday → Sunday)
        • Expected date = next Thursday (next delivery day)
        """
        self.product.sale_delay = 3  # Sunday
        order = self._create_order(self.customer_time_window)
        self.assertEqual(
            fields.Datetime.to_string(order.expected_date),
            "2020-04-09 00:00:00",
            "Thursday is the next available day, after the sale delay",
        )

    @freeze_time("2020-04-02 10:00:00")  # Thursday
    def test_no_warning_on_picking_scheduled_date(self):
        """Verify picking scheduled date matches order expected date.

        • Order confirmed with delivery window logic
        • Picking scheduled_date = order expected_date
        • No delivery window warning raised
        """
        self.product.sale_delay = 3  # Sunday
        order = self._create_order(self.customer_time_window)
        # Same as test_expected_date_time_windows_with_sale_delay
        # order.expected_date = "2020-04-09 00:00:00"
        order.action_confirm()
        self.assertEqual(
            fields.Datetime.to_string(order.picking_ids.scheduled_date),
            "2020-04-09 00:00:00",
            "The scheduled date is the expected date",
        )
        self.assertFalse(order.picking_ids.partner_delivery_window_warning)

    @freeze_time("2020-04-01 10:00:00")  # Wednesday
    def test_warning_on_commitment_date_not_fitting_delivery_window(self):
        """Verify warning is shown if commitment date doesn't fit the delivery window.

        The chosen date is Friday, not fitting the delivery window.
        """
        order = self._create_order(self.customer_time_window)
        with Form(order) as form, self.assertLogs("odoo.tests.form") as cm:
            form.commitment_date = "2020-04-03 10:00:00"  # Friday
            self.assertTrue(
                cm.output[0].startswith("WARNING:odoo.tests.form.onchange:")
            )
            self.assertIn("Customer delivery preference not met", cm.output[0])
            self.assertEqual(
                form.commitment_date,
                "2020-04-03 10:00:00",
                "The user input is respected, though",
            )

    @freeze_time("2020-04-01 10:00:00")  # Wednesday
    def test_warning_on_commitment_date_fitting_delivery_window(self):
        """No warning is shown if commitment date fits the delivery window."""
        order = self._create_order(self.customer_time_window)
        with Form(order) as form, self.assertNoLogs("odoo.tests.form"):
            form.commitment_date = "2020-04-02 10:00:00"
