# Copyright 2020 Camptocamp
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from freezegun import freeze_time

from .common import PartnerDeliveryWindowCommon


class TestPartnerDeliveryWindow(PartnerDeliveryWindowCommon):
    @freeze_time("2020-04-02")  # Thursday
    def test_delivery_window_warning(self):
        # No warning with anytime
        anytime_picking = self._create_delivery_picking(self.customer_anytime)
        anytime_picking.scheduled_date = "2020-04-03"  # Friday
        anytime_picking._compute_partner_delivery_window_warning()
        self.assertFalse(anytime_picking.partner_delivery_window_warning)
        # No warning on friday
        workdays_picking = self._create_delivery_picking(self.customer_working_days)
        workdays_picking.scheduled_date = "2020-04-03"  # Friday
        workdays_picking._compute_partner_delivery_window_warning()
        self.assertFalse(workdays_picking.partner_delivery_window_warning)
        # But warning on saturday
        workdays_picking.scheduled_date = "2020-04-04"  # Saturday
        workdays_picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on working days",
            workdays_picking.partner_delivery_window_warning,
        )
        # No warning on preferred time window
        time_window_picking = self._create_delivery_picking(self.customer_time_window)
        time_window_picking.scheduled_date = "2020-04-04"  # Saturday
        time_window_picking._compute_partner_delivery_window_warning()
        self.assertFalse(time_window_picking.partner_delivery_window_warning)
        time_window_picking.scheduled_date = "2020-04-03"  # Friday
        time_window_picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on following time windows",
            time_window_picking.partner_delivery_window_warning,
        )
        # Warning when no scheduled date
        time_window_picking.scheduled_date = False
        time_window_picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "No scheduled date is set on the picking, cannot check",
            time_window_picking.partner_delivery_window_warning,
        )

    @freeze_time("2020-04-02 07:59:59")  # Thursday
    def test_with_timezone_dst(self):
        # Define customer to allow shipping only between 10.00am and 4.00pm
        # in tz 'Europe/Brussels' (GMT+1 or GMT+2 during DST)
        self.customer_time_window.tz = "Europe/Brussels"
        self.customer_time_window.delivery_time_window_ids.write(
            {"time_window_start": 10.0, "time_window_end": 16.0}
        )
        # Test DST
        #
        # Frozen time is in UTC so 2020-04-02 07:59:59 == 2020-04-02 09:59:59
        #  in Brussels which is preferred
        picking = self._create_delivery_picking(self.customer_time_window)
        picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on following time windows",
            picking.partner_delivery_window_warning,
        )
        # Scheduled date is in UTC so 2020-04-02 08:00:00 == 2020-04-02 10:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 08:00:00"
        picking._compute_partner_delivery_window_warning()
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-04-02 13:59:59 == 2020-04-02 15:59:59
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 13:59:59"
        picking._compute_partner_delivery_window_warning()
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-04-02 14:00:00 == 2020-04-02 16:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 14:00:00"
        picking._compute_partner_delivery_window_warning()
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-04-02 14:00:01 == 2020-04-02 16:00:01
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 14:00:01"
        picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on following time windows",
            picking.partner_delivery_window_warning,
        )

    @freeze_time("2020-03-26 08:59:59")  # Thursday
    def test_with_timezone_no_dst(self):
        # Define customer to allow shipping only between 10.00am and 4.00pm
        # in tz 'Europe/Brussels' (GMT+1 or GMT+2 during DST)
        self.customer_time_window.tz = "Europe/Brussels"
        self.customer_time_window.delivery_time_window_ids.write(
            {"time_window_start": 10.0, "time_window_end": 16.0}
        )
        # Test No-DST
        #
        # Frozen time is in UTC so 2020-03-26 08:59:59 == 2020-04-02 09:59:59
        #  in Brussels which is preferred
        picking = self._create_delivery_picking(self.customer_time_window)
        picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on following time windows",
            picking.partner_delivery_window_warning,
        )
        # Scheduled date is in UTC so 2020-03-26 09:00:00 == 2020-04-02 10:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 09:00:00"
        picking._compute_partner_delivery_window_warning()
        # No warning since we're in the timeframe
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-03-26 14:59:59 == 2020-04-02 15:59:59
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 14:59:59"
        picking._compute_partner_delivery_window_warning()
        # No warning since we're in the timeframe
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-03-26 15:00:00 == 2020-04-02 16:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 15:00:00"
        picking._compute_partner_delivery_window_warning()
        self.assertFalse(picking.partner_delivery_window_warning)
        # Scheduled date is in UTC so 2020-03-26 15:00:01 == 2020-04-02 16:00:01
        #  in Brussels which is not preferred
        picking.scheduled_date = "2020-03-26 15:00:01"
        picking._compute_partner_delivery_window_warning()
        self.assertIn(
            "the partner is set to prefer deliveries on following time windows",
            picking.partner_delivery_window_warning,
        )

    def test_copy_partner_with_time_window_ids(self):
        copied_partner = self.customer_time_window.copy()
        expecting = len(self.customer_time_window.delivery_time_window_ids)
        self.assertEqual(len(copied_partner.delivery_time_window_ids), expecting)
        copied_partner = self.customer_working_days.copy()
        self.assertFalse(copied_partner.delivery_time_window_ids)

    def test_weekdays_anytime(self):
        self.assertEqual(
            self.customer_anytime.delivery_time_weekdays, {0, 1, 2, 3, 4, 5, 6}
        )

    def test_weekdays_working_days(self):
        self.assertEqual(
            self.customer_working_days.delivery_time_weekdays, {0, 1, 2, 3, 4}
        )

    def test_weekdays_time_window(self):
        self.assertEqual(self.customer_time_window.delivery_time_weekdays, {3, 5})

    def test_is_in_delivery_window(self):
        # window for Thu and Sat
        self.customer_time_window.delivery_time_window_ids.write(
            {"time_window_start": 10.0, "time_window_end": 16.0}
        )
        # Friday
        date = datetime.date.fromisoformat("2020-04-03")
        self.assertFalse(self.customer_time_window.is_in_delivery_window(date))
        # Saturday
        date = datetime.date.fromisoformat("2020-04-04")
        self.assertTrue(self.customer_time_window.is_in_delivery_window(date))
        date = datetime.datetime.fromisoformat("2020-04-04 09:00:00")
        self.assertFalse(self.customer_time_window.is_in_delivery_window(date))
        date = datetime.datetime.fromisoformat("2020-04-04 10:00:00")
        self.assertTrue(self.customer_time_window.is_in_delivery_window(date))
        date = datetime.datetime.fromisoformat("2020-04-04 16:00:00")
        self.assertTrue(self.customer_time_window.is_in_delivery_window(date))
        date = datetime.datetime.fromisoformat("2020-04-04 17:00:00")
        self.assertFalse(self.customer_time_window.is_in_delivery_window(date))
