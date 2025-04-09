# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon


class TestPartnerDeliveryWindow(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
