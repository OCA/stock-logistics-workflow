# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.tests import SavepointCase


class TestPartnerDeliveryWindow(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer = cls.env["res.partner"].create(
            {"name": "ACME", "delivery_time_preference": "anytime"}
        )
        cls.customer_shipping = cls.env["res.partner"].create(
            {
                "name": "Delivery address",
                "parent_id": cls.customer.id,
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
        cust_picking = self._create_delivery_picking(self.customer)
        cust_picking.scheduled_date = "2020-04-03"  # Friday
        onchange_res = cust_picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        # No warning on preferred time window
        cust_ship_picking = self._create_delivery_picking(self.customer_shipping)
        cust_ship_picking.scheduled_date = "2020-04-04"  # Saturday
        onchange_res = cust_ship_picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)
        cust_ship_picking.scheduled_date = "2020-04-03"  # Friday
        onchange_res = cust_ship_picking._onchange_scheduled_date()
        self.assertTrue("warning" in onchange_res.keys())

    @freeze_time("2020-04-02 07:59:59")  # Thursday
    def test_with_timezone_dst(self):
        # Define customer to allow shipping only between 10.00am and 4.00pm
        # in tz 'Europe/Brussels' (GMT+1 or GMT+2 during DST)
        self.customer_shipping.tz = "Europe/Brussels"
        self.customer_shipping.delivery_time_window_ids.write(
            {"time_window_start": 10.0, "time_window_end": 16.0}
        )
        # Test DST
        #
        # Frozen time is in UTC so 2020-04-02 07:59:59 == 2020-04-02 09:59:59
        #  in Brussels which is preferred
        picking = self._create_delivery_picking(self.customer_shipping)
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
        #  in Brussels which is not preferred
        picking.scheduled_date = "2020-04-02 14:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
        )

    @freeze_time("2020-03-26 08:59:59")  # Thursday
    def test_with_timezone_no_dst(self):
        # Define customer to allow shipping only between 10.00am and 4.00pm
        # in tz 'Europe/Brussels' (GMT+1 or GMT+2 during DST)
        self.customer_shipping.tz = "Europe/Brussels"
        self.customer_shipping.delivery_time_window_ids.write(
            {"time_window_start": 10.0, "time_window_end": 16.0}
        )
        # Test No-DST
        #
        # Frozen time is in UTC so 2020-03-26 08:59:59 == 2020-04-02 09:59:59
        #  in Brussels which is preferred
        picking = self._create_delivery_picking(self.customer_shipping)
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
        self.assertTrue(
            isinstance(onchange_res, dict) and "warning" in onchange_res.keys()
        )
