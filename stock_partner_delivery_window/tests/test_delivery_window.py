# Copyright 2020 Camptocamp
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import warnings

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartnerDeliveryWindow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer_anytime = cls.env["res.partner"].create(
            {"name": "Anytime", "delivery_time_preference": "anytime"}
        )
        cls.customer_working_days = cls.env["res.partner"].create(
            {"name": "Working Days", "delivery_time_preference": "workdays"}
        )
        cls.customer_time_window = cls.env["res.partner"].create(
            {
                "name": "Time Window",
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 0.00,
                            "time_window_end": 23.99,
                            "time_window_weekday_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env.ref(
                                            "base_time_window.time_weekday_thursday"
                                        ).id,
                                        cls.env.ref(
                                            "base_time_window.time_weekday_saturday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )
        cls.product = cls.env.ref("product.product_product_9")
        cls.picking_type_delivery = cls.env.ref("stock.picking_type_out")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")

    def _create_delivery_picking(self, partner):
        return self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customers.id,
                "picking_type_id": self.picking_type_delivery.id,
            }
        )

    @freeze_time("2020-04-02")  # Thursday
    def test_delivery_window_warning(self):
        # No warning with anytime
        anytime_picking = self._create_delivery_picking(self.customer_anytime)
        anytime_picking.scheduled_date = "2020-04-03"  # Friday
        onchange_res = anytime_picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # No warning on friday
        workdays_picking = self._create_delivery_picking(self.customer_working_days)
        workdays_picking.scheduled_date = "2020-04-03"  # Friday
        onchange_res = workdays_picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # But warning on saturday
        workdays_picking.scheduled_date = "2020-04-04"  # Saturday
        onchange_res = workdays_picking._onchange_scheduled_date()
        self.assertIn("warning", onchange_res)
        self.assertIn(
            "the partner is set to prefer deliveries on working days",
            onchange_res["warning"]["message"],
        )
        # No warning on preferred time window
        time_window_picking = self._create_delivery_picking(self.customer_time_window)
        time_window_picking.scheduled_date = "2020-04-04"  # Saturday
        onchange_res = time_window_picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        time_window_picking.scheduled_date = "2020-04-03"  # Friday
        onchange_res = time_window_picking._onchange_scheduled_date()
        self.assertTrue("warning" in onchange_res.keys())

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
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
        )
        # Scheduled date is in UTC so 2020-04-02 08:00:00 == 2020-04-02 10:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 08:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-04-02 13:59:59 == 2020-04-02 15:59:59
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 13:59:59"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-04-02 14:00:00 == 2020-04-02 16:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 14:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-04-02 14:00:01 == 2020-04-02 16:00:01
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-04-02 14:00:01"
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
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
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
        )
        # Scheduled date is in UTC so 2020-03-26 09:00:00 == 2020-04-02 10:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 09:00:00"
        onchange_res = picking._onchange_scheduled_date()
        # No warning since we're in the timeframe
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-03-26 14:59:59 == 2020-04-02 15:59:59
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 14:59:59"
        onchange_res = picking._onchange_scheduled_date()
        # No warning since we're in the timeframe
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-03-26 15:00:00 == 2020-04-02 16:00:00
        #  in Brussels which is preferred
        picking.scheduled_date = "2020-03-26 15:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # Scheduled date is in UTC so 2020-03-26 15:00:01 == 2020-04-02 16:00:01
        #  in Brussels which is not preferred
        picking.scheduled_date = "2020-03-26 15:00:01"
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
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

    def test_check_delivery_time_preference_constraint(self):
        # Creation without windows should fail
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {
                    "name": "NoWindow",
                    "delivery_time_preference": "time_windows",
                }
            )
        # If we remove all windows from an existing partner it should also fail
        partner = self.customer_time_window
        # Make sure it has windows
        self.assertTrue(partner.delivery_time_window_ids)
        with self.assertRaises(ValidationError):
            partner.delivery_time_window_ids = [(5, 0, 0)]

    def test_get_delivery_time_format_string_warning(self):
        partner = self.customer_anytime
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fmt = partner._get_delivery_time_format_string()
            # the format string should be translatable
            self.assertEqual(fmt, "From %(start)s to %(end)s")
            # it should have raised a DeprecationWarning
            self.assertTrue(any(item.category is DeprecationWarning for item in w))

    def test_get_delivery_time_description(self):
        # ANYTIME branch
        desc_map = self.customer_anytime.get_delivery_time_description()
        desc = desc_map[self.customer_anytime.id]
        lines = desc.split("\n")

        self.assertEqual(len(lines), 2)
        self.assertRegex(desc, r"Saturday:.*12:00 AM.*11:59 PM")
        self.assertRegex(desc, r"Sunday:.*12:00 AM.*11:59 PM")

        # WORKDAYS branch
        desc_map = self.customer_working_days.get_delivery_time_description()
        desc = desc_map[self.customer_working_days.id]
        lines = desc.split("\n")

        self.assertEqual(len(lines), 2)
        self.assertRegex(desc, r"Saturday:.*12:00 AM.*11:59 PM")
        self.assertRegex(desc, r"Sunday:.*12:00 AM.*11:59 PM")

        # TIME_WINDOWS branch
        desc_map = self.customer_time_window.get_delivery_time_description()
        desc = desc_map[self.customer_time_window.id]
        lines = desc.split("\n")

        self.assertEqual(len(lines), 2)
        self.assertRegex(desc, r"Saturday:.*12:00 AM.*11:59 PM")
        self.assertRegex(desc, r"Sunday:.*12:00 AM.*11:59 PM")
