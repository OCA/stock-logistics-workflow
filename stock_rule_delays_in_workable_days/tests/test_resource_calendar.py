# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

from ..models.weekday import WeekdaysEnum


def attendance_ids(*weekdays: WeekdaysEnum):
    return [
        (
            0,
            0,
            {
                "name": weekday.name,
                "dayofweek": str(weekday.value),
                "hour_from": 8,
                "hour_to": 12,
            },
        )
        for weekday in weekdays
    ]


class TestResourceCalendarAddWorkingDaysToDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Working week days: Mo Tu We Th Fr Sa Su
        #          calendar:  x  x     x  x
        # From 8 to 12 am
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                ),
                "leave_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Leaves",
                            "date_from": "2024-01-10 00:00:00",
                            "date_to": "2024-01-10 23:59:59",
                        },
                    )
                ],
            }
        )

    def test_add_zero_working_days(self):
        date = fields.Datetime.to_datetime("2024-01-01 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(date, 0, include_given_date=False),
            date,
        )

    def test_add_zero_working_days_including_given_date(self):
        date = fields.Datetime.to_datetime("2024-01-01 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(date, 0, include_given_date=True),
            date,
        )

    def test_add_one_working_day(self):
        wednesday = fields.Datetime.to_datetime("2024-01-03 10:00:00")
        thursday = fields.Datetime.to_datetime("2024-01-04 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, 1, include_given_date=False
            ),
            thursday,
        )

    def test_add_one_working_day_including_given_date(self):
        wednesday = fields.Datetime.to_datetime("2024-01-03 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, 1, include_given_date=True
            ),
            wednesday,
        )

    def test_add_one_working_day_before_weekend(self):
        friday = fields.Datetime.to_datetime("2024-01-05 10:00:00")
        monday = fields.Datetime.to_datetime("2024-01-08 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(friday, 1, include_given_date=False),
            monday,
        )

    def test_add_one_working_day_during_weekend(self):
        saturday = fields.Datetime.to_datetime("2024-01-06 10:00:00")
        monday = fields.Datetime.to_datetime("2024-01-08 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                saturday, 1, include_given_date=False
            ),
            monday,
        )

    def test_add_one_working_day_before_leave(self):
        tuesday = fields.Datetime.to_datetime("2024-01-09 10:00:00")
        thursday = fields.Datetime.to_datetime("2024-01-11 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                tuesday, 1, include_given_date=False
            ),
            thursday,
        )

    def test_add_one_working_day_during_leave(self):
        wednesday = fields.Datetime.to_datetime("2024-01-10 10:00:00")
        thursday = fields.Datetime.to_datetime("2024-01-11 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, 1, include_given_date=False
            ),
            thursday,
        )

    def test_subtract_one_working_day(self):
        wednesday = fields.Datetime.to_datetime("2024-01-03 10:00:00")
        tuesday = fields.Datetime.to_datetime("2024-01-02 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, -1, include_given_date=False
            ),
            tuesday,
        )

    def test_subtract_one_working_day_including_given_date(self):
        wednesday = fields.Datetime.to_datetime("2024-01-03 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, -1, include_given_date=True
            ),
            wednesday,
        )

    def test_subtract_one_working_day_before_weekend(self):
        monday = fields.Datetime.to_datetime("2024-01-01 10:00:00")
        friday = fields.Datetime.to_datetime("2023-12-29 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                monday, -1, include_given_date=False
            ),
            friday,
        )

    def test_subtract_one_working_day_during_weekend(self):
        sunday = fields.Datetime.to_datetime("2023-12-31 10:00:00")
        friday = fields.Datetime.to_datetime("2023-12-29 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                sunday, -1, include_given_date=False
            ),
            friday,
        )

    def test_subtract_one_working_day_before_leave(self):
        thursday = fields.Datetime.to_datetime("2024-01-11 10:00:00")
        tuesday = fields.Datetime.to_datetime("2024-01-09 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                thursday, -1, include_given_date=False
            ),
            tuesday,
        )

    def test_subtract_one_working_day_during_leave(self):
        wednesday = fields.Datetime.to_datetime("2024-01-10 10:00:00")
        tuesday = fields.Datetime.to_datetime("2024-01-09 10:00:00")
        self.assertEqual(
            self.calendar.add_working_days_to_date(
                wednesday, -1, include_given_date=False
            ),
            tuesday,
        )


class TestResourceCalendarIsAWorkingDay(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Working week days: Mo Tu We Th Fr Sa Su
        #          calendar:  x  x  x  x  x
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                ),
                "leave_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Leaves",
                            "date_from": "2024-01-01 00:00:00",
                            "date_to": "2024-01-01 23:59:59",
                        },
                    )
                ],
            }
        )

    def test_working_day(self):
        monday = fields.Datetime.to_datetime("2024-01-08")
        self.assertTrue(self.calendar.is_a_working_day(monday))

        tuesday = fields.Datetime.to_datetime("2024-01-09")
        self.assertTrue(self.calendar.is_a_working_day(tuesday))

        wednesday = fields.Datetime.to_datetime("2024-01-10")
        self.assertTrue(self.calendar.is_a_working_day(wednesday))

        thursday = fields.Datetime.to_datetime("2024-01-11")
        self.assertTrue(self.calendar.is_a_working_day(thursday))

        friday = fields.Datetime.to_datetime("2024-01-12")
        self.assertTrue(self.calendar.is_a_working_day(friday))

    def test_weekend(self):
        saturday = fields.Datetime.to_datetime("2023-12-31")
        self.assertFalse(self.calendar.is_a_working_day(saturday))

        sunday = fields.Datetime.to_datetime("2023-12-30")
        self.assertFalse(self.calendar.is_a_working_day(sunday))

    def test_leave_day(self):
        monday_new_year_day = fields.Datetime.to_datetime("2024-01-01")
        self.assertFalse(self.calendar.is_a_working_day(monday_new_year_day))


class TestResourceCalendarComputeTransferDatesFromTargetSentDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Working week days: Mo Tu We Th Fr Sa Su
        #   sender_calendar:  x  x     x  x  x  x
        # receiver_calendar:  x  x  x  x  x     x
        cls.sender_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Sender Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Saturday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )
        cls.receiver_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Receiver Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )

    def test_send_from_wednesday_with_zero_days_lead_time(self):
        # Wednesday
        target_sent_date = fields.Datetime.to_datetime("2024-01-03")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_sent_date(
            target_sent_date,
            0,
            self.sender_calendar,
            self.receiver_calendar,
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # The Thursday after Wednesday
            fields.Datetime.to_datetime("2024-01-04"),
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # The Thursday after Wednesday
            fields.Datetime.to_datetime("2024-01-04"),
        )

    def test_send_from_wednesday_with_two_days_lead_time(self):
        # Wednesday
        target_sent_date = fields.Datetime.to_datetime("2024-01-03")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_sent_date(
            target_sent_date,
            2,
            self.sender_calendar,
            self.receiver_calendar,
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # The Thursday after Wednesday
            fields.Datetime.to_datetime("2024-01-04"),
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # The Sunday after Wednesday
            fields.Datetime.to_datetime("2024-01-07"),
        )

    def test_send_from_wednesday_with_two_days_lead_time_no_calendars(self):
        # Wednesday
        target_sent_date = fields.Datetime.to_datetime("2024-01-03")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_sent_date(
            target_sent_date,
            2,
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # The same day as the target sent date
            fields.Datetime.to_datetime("2024-01-03"),
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # Two days after the target sent date
            fields.Datetime.to_datetime("2024-01-05"),
        )

    def test_invalid_lead_time(self):
        target_sent_date = fields.Datetime.to_datetime("2024-01-03")
        with self.assertRaisesRegex(
            ValidationError, "The lead time must be a positive number."
        ):
            self.env["resource.calendar"].compute_transfer_dates_from_target_sent_date(
                target_sent_date,
                -1,
            )


class TestResourceCalendarComputeTransferDatesFromTargetReceivedDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Working week days: Mo Tu We Th Fr Sa Su
        #   sender_calendar:  x  x     x  x  x  x
        # receiver_calendar:  x  x  x  x  x     x
        cls.sender_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Sender Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Saturday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )
        cls.receiver_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Receiver Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )

    def test_receive_by_saturday_with_zero_days_lead_time(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_received_date(
            target_received_date,
            0,
            self.sender_calendar,
            self.receiver_calendar,
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # The Friday prior to Saturday
            fields.Datetime.to_datetime("2024-01-05"),
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # The Friday prior to Saturday
            fields.Datetime.to_datetime("2024-01-05"),
        )

    def test_receive_by_saturday_with_two_days_lead_time(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_received_date(
            target_received_date,
            2,
            self.sender_calendar,
            self.receiver_calendar,
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # The Friday prior to Saturday
            fields.Datetime.to_datetime("2024-01-05"),
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # The Tuesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-02"),
        )

    def test_receive_by_saturday_with_two_days_lead_time_no_calendars(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        transfer_dates = self.env[
            "resource.calendar"
        ].compute_transfer_dates_from_target_received_date(
            target_received_date,
            2,
        )
        self.assertEqual(
            transfer_dates["expected_received_date"],
            # The same day as the target received date
            fields.Datetime.to_datetime("2024-01-06"),
        )
        self.assertEqual(
            transfer_dates["actual_sent_date"],
            # Two days before the target received date
            fields.Datetime.to_datetime("2024-01-04"),
        )

    def test_invalid_lead_time(self):
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        with self.assertRaisesRegex(
            ValidationError, "The lead time must be a positive number."
        ):
            self.env[
                "resource.calendar"
            ].compute_transfer_dates_from_target_received_date(
                target_received_date,
                -1,
            )


class TestResourceCalendarComputeOrderDatesFromTargetReceivedDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #    Working week days: Mo Tu We Th Fr Sa Su
        #    supplier_calendar:  x  x     x  x  x  x
        #  supplier_order_days:        x     x
        #  supplier_lead_times:     1  2     3
        #                           2  3     4
        # destination_calendar:  x  x  x     x     x
        cls.supplier_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Supplier Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Saturday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )
        cls.lead_times_by_day = {
            WeekdaysEnum.Tuesday: [1, 2],
            WeekdaysEnum.Wednesday: [2, 3],
            WeekdaysEnum.Friday: [3, 4],
        }
        cls.destination_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Destination Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )

    def test_compute_inverted_lead_times_by_day(self):
        self.assertEqual(
            self.env["resource.calendar"]._compute_inverted_lead_times_by_day(
                self.lead_times_by_day
            ),
            {
                WeekdaysEnum.Monday: [3],
                WeekdaysEnum.Tuesday: [4],
                WeekdaysEnum.Wednesday: [1],
                WeekdaysEnum.Thursday: [2],
                WeekdaysEnum.Friday: [2],
                WeekdaysEnum.Saturday: [3],
                WeekdaysEnum.Sunday: [],
            },
        )

    def test_receive_by_saturday(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-01")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # The Wednesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-03"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The Tuesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-02"),
        )

    def test_compute_order_dates_from_target_received_date_no_dest_calendar(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-01")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.env["resource.calendar"].browse(),
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # The Thursday prior to Saturday because no dest calendar
            fields.Datetime.to_datetime("2024-01-04"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The Tuesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-02"),
        )

    def test_receive_by_saturday_no_calendars(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-01")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # The same day
            fields.Datetime.to_datetime("2024-01-06"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The Wednesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-03"),
        )

    def test_receive_by_saturday_no_match(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-05")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertIsNone(order_dates)


class TestResourceCalendarComputePossibleOrderDatesFromTargetReceivedDate(
    SavepointCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lead_times_by_day = {
            WeekdaysEnum.Monday: [3],
            WeekdaysEnum.Tuesday: [3],
            WeekdaysEnum.Thursday: [3],
            WeekdaysEnum.Friday: [3],
            WeekdaysEnum.Saturday: [3],
            WeekdaysEnum.Sunday: [3],
        }
        cls.received_date = fields.Datetime.to_datetime("2024-01-06")
        cls.supplier_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Supplier Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Saturday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )

    def test_compute_inverted_lead_times_by_date(self):
        # A Saturday
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        possible_order_dates = self.env[
            "resource.calendar"
        ]._compute_possible_order_dates_from_target_received_date(
            self.lead_times_by_day, target_received_date, self.supplier_calendar
        )
        self.assertEqual(
            possible_order_dates,
            [fields.Datetime.to_datetime("2024-01-02")],
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar._compute_inverted_lead_times_by_day",
        return_value={WeekdaysEnum.Saturday: [3, 8]},
    )
    def test_compute_inverted_lead_times_by_date_no_calendar(
        self, mock_compute_inverted_lead_times_by_day
    ):
        # A Saturday
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        possible_order_dates = self.env[
            "resource.calendar"
        ]._compute_possible_order_dates_from_target_received_date(
            self.lead_times_by_day, target_received_date
        )
        self.assertEqual(
            possible_order_dates,
            [
                fields.Datetime.to_datetime("2023-12-29"),
                fields.Datetime.to_datetime("2024-01-03"),
            ],
        )
        # Should be called once
        mock_compute_inverted_lead_times_by_day.assert_called_once()
        mock_compute_inverted_lead_times_by_day.assert_called_with(
            self.lead_times_by_day
        )


class TestResourceCalendarComputeOrderDatesFromTargetReceivedDateInWorkingDays(
    SavepointCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #    Working week days: Mo Tu We Th Fr Sa Su
        #    supplier_calendar:  x  x     x  x  x  x
        #  supplier_order_days:  x  x     x  x
        #  supplier_lead_times:  2  2     2  2
        # destination_calendar:  x  x  x  x  x     x
        cls.supplier_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Supplier Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Saturday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )
        cls.lead_times_by_day = {
            WeekdaysEnum.Monday: [2],
            WeekdaysEnum.Tuesday: [2],
            WeekdaysEnum.Thursday: [2],
            WeekdaysEnum.Friday: [2],
        }
        cls.destination_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Destination Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                    WeekdaysEnum.Sunday,
                ),
            }
        )

    def test_receive_by_saturday(self):
        # Saturday 2024-01-06
        target_received_date = fields.Datetime.to_datetime("2024-01-06")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-01")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date_working_days(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # The Friday prior to Saturday
            fields.Datetime.to_datetime("2024-01-05"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The Tuesday prior to Saturday
            fields.Datetime.to_datetime("2024-01-02"),
        )

    def test_receive_by_tuesday(self):
        # Tuesday 2024-01-09
        target_received_date = fields.Datetime.to_datetime("2024-01-09")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-06")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date_working_days(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # The Friday prior to Tuesday
            fields.Datetime.to_datetime("2024-01-07"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The Thursday prior to Tuesday
            fields.Datetime.to_datetime("2024-01-05"),
        )

    def test_receive_by_tuesday_no_match(self):
        # Tuesday 2024-01-09
        target_received_date = fields.Datetime.to_datetime("2024-01-09")
        lower_acceptable_received_date = fields.Datetime.to_datetime("2024-01-08")
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date_working_days(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertIsNone(order_dates)

    def test_receive_by_sunday(self):
        target_received_date = fields.Datetime.to_datetime("2024-01-14 12:00:00")
        lower_acceptable_received_date = fields.Datetime.to_datetime(
            "2024-01-14 15:00:00"
        )
        order_dates = self.env[
            "resource.calendar"
        ].compute_order_dates_from_target_received_date_working_days(
            target_received_date,
            lower_acceptable_received_date,
            self.lead_times_by_day,
            self.supplier_calendar,
            self.destination_calendar,
        )
        self.assertEqual(
            order_dates["expected_delivery_date"],
            # Sunday
            fields.Datetime.to_datetime("2024-01-14 12:00:00"),
        )
        self.assertEqual(
            order_dates["actual_order_date"],
            # The friday prior to Sunday
            fields.Datetime.to_datetime("2024-01-12 12:00:00"),
        )
