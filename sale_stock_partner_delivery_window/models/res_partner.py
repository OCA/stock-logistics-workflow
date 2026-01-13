# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

import pytz

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.date_utils import start_of


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _next_available_delivery_date(
        self, from_date: date | datetime | None = None
    ) -> datetime:
        """Compute the next available delivery date"""
        # If from_date is not provided, use the current datetime
        if from_date is None:  # pragma: no cover
            from_date = fields.Datetime.now()
        # Pre-compute the from_datetime, in case from_date is a `date`
        # We use the start of the day in the partner's timezone
        tz = pytz.timezone(self.tz or self.env.company.partner_id.tz or "UTC")
        from_datetime_tz_aware = tz.localize(fields.Datetime.to_datetime(from_date))
        from_datetime = from_datetime_tz_aware.astimezone(pytz.utc).replace(tzinfo=None)
        # If the delivery is anytime, simply return the from_datetime
        if self.delivery_time_preference == "anytime":
            return from_datetime
        # If it's workdays, we need to check if the from_datetime is a weekday
        # or adjust accordingly
        elif self.delivery_time_preference == "workdays":
            weekday = from_datetime_tz_aware.weekday()
            if weekday <= 4:
                return from_datetime
            return from_datetime + timedelta(days=7 - weekday)
        # If we're using time windows, we search for the next available slot
        # We use the tz-aware datetime, as windows are expressed in the partner's tz
        elif self.delivery_time_preference == "time_windows":
            for days_to_add in range(7 + 1):
                next_date = (
                    start_of(
                        from_datetime_tz_aware + timedelta(days=days_to_add), "day"
                    )
                    if days_to_add
                    else from_datetime_tz_aware
                )
                for window in self.delivery_time_window_ids:
                    # Check if the window is available for this day
                    weekdays = set(
                        map(int, window.time_window_weekday_ids.mapped("name"))
                    )
                    if next_date.weekday() not in weekdays:
                        continue
                    start_time = window.get_time_window_start_time()
                    end_time = window.get_time_window_end_time()
                    # If we're adding days (evaluating today), and we're providing time,
                    # we must ensure it's within the window's time range, or at least
                    # the day range hasn't passed yet
                    if not days_to_add:
                        if not isinstance(from_date, datetime):
                            return from_datetime
                        elif start_time <= from_datetime_tz_aware.time() <= end_time:
                            return from_datetime
                        elif from_datetime_tz_aware.time() > end_time:
                            continue
                    # Otherwise, since we're looking at days ahead, simply pick the
                    # window's start time
                    return (
                        datetime.combine(next_date, start_time)
                        .astimezone(pytz.utc)
                        .replace(tzinfo=None)
                    )
        else:  # pragma: no cover
            raise ValueError(
                self.env._(
                    "Invalid delivery time preference: %s",
                    self.delivery_time_preference,
                )
            )
        raise UserError(self.env._("No available delivery date found"))
