# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from freezegun import freeze_time

from .common import PartnerDeliveryWindowCommon


class TestPartnerDeliveryWindowDate(PartnerDeliveryWindowCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.startClassPatcher(
            mock.patch(
                "odoo.addons.stock_partner_delivery_window.models.stock_picking.StockPicking._planned_delivery_date",
                new=lambda self: self.scheduled_date and self.scheduled_date.date(),
            )
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
        # Warning when no scheduled date
        with mock.patch(
            "odoo.addons.stock_partner_delivery_window.models.stock_picking.StockPicking._planned_delivery_date",
            return_value=False,
        ):
            time_window_picking._compute_partner_delivery_window_warning()
            self.assertIn(
                "No delivery date is set on the picking, cannot check",
                time_window_picking.partner_delivery_window_warning,
            )
