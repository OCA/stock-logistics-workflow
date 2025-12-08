# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from .common import PartnerDeliveryWindowCommon


class TestPartnerDeliveryWindowDate(PartnerDeliveryWindowCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models.planned_delivery_date import StockPicking

        cls.loader.update_registry((StockPicking,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super().tearDownClass()

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
