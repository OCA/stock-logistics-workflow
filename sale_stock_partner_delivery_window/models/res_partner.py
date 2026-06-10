# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta

import pytz

from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _to_partner_delivery_datetime(self, from_date, tz):
        """Convert a datetime to partner local datetime.

        :param from_date: date or datetime to convert.
        :param tz: partner delivery window timezone string.
        :return: timezone aware datetime in the partner timezone.
        """
        timezone = pytz.timezone(tz)
        if isinstance(from_date, datetime):
            return pytz.utc.localize(from_date).astimezone(timezone)
        return timezone.localize(fields.Datetime.to_datetime(from_date))

    def _next_available_delivery_date(
        self, from_date: date | datetime | None = None
    ) -> datetime:
        """Compute the next available delivery datetime in Odoo UTC format.

        Partner delivery preferences are expressed in the partner delivery
        timezone, while Odoo datetime fields are stored as naive UTC datetimes.
        This method therefore accepts either:

        * a naive UTC ``datetime`` coming from Odoo, such as a sale order
          ``commitment_date`` or a sale line expected date;
        * a ``date`` value, which is interpreted as a date in the partner
          delivery timezone;
        * no value, in which case the current Odoo UTC datetime is used.

        The returned value is always a naive UTC ``datetime`` suitable for Odoo
        datetime fields.

        Concrete examples:

        * ``anytime``: ``2026-06-11 11:00:00`` UTC is already valid, so it is
          returned unchanged.
        * ``workdays``: a Saturday input is moved forward to Monday while
          keeping the original UTC time.
        * ``time_windows``: with partner timezone ``Europe/Zurich`` and a
          Wednesday ``09:00-17:00`` window, Wednesday ``09:00`` local in June is
          returned as ``07:00:00`` UTC. If Thursday ``13:00`` local
          is requested for a Wednesday only partner,
          the method returns the next Wednesday window start.
        """
        # If no anchor date is provided, use the current Odoo UTC datetime.
        if from_date is None:  # pragma: no cover
            from_date = fields.Datetime.now()
        tz = self.delivery_window_tz
        # Build the concrete pytz timezone object used for future local dates.
        timezone = pytz.timezone(tz)
        # Normalize the input into an Odoo-style naive UTC datetime.
        from_datetime = fields.Datetime.to_datetime(from_date)
        # Convert the same point, or date, into the partner delivery timezone.
        from_datetime_tz_aware = self._to_partner_delivery_datetime(from_date, tz)
        # ``anytime`` means there is no delivery window adjustment to apply.
        if self.delivery_time_preference == "anytime":
            # Return the normalized UTC datetime unchanged.
            return from_datetime
        # ``workdays`` only constrains the partner local weekday.
        elif self.delivery_time_preference == "workdays":
            # Use the partner local weekday, where Monday is 0 and Sunday is 6.
            weekday = from_datetime_tz_aware.weekday()
            # Monday through Friday are already valid delivery days.
            if weekday <= 4:
                # Keep the exact original UTC datetime.
                return from_datetime
            # Weekend dates are moved to next Monday, preserving the UTC time.
            return from_datetime + timedelta(days=7 - weekday)
        # ``time_windows`` constrains both the partner local weekday and time.
        elif self.delivery_time_preference == "time_windows":
            # Search today plus the next seven days, enough to cover weekly windows.
            for days_to_add in range(7 + 1):
                # For day zero, keep the precise partner local input datetime.
                next_date = from_datetime_tz_aware
                # For future days, start from local midnight of that candidate day.
                if days_to_add:
                    # Compute the candidate date in the partner local calendar.
                    candidate_date = from_datetime_tz_aware.date() + timedelta(
                        days=days_to_add
                    )
                    # Keep midnight timezone aware; naive midnight would be UTC-like.
                    next_date = timezone.localize(
                        datetime.combine(candidate_date, datetime.min.time())
                    )
                # Try every configured delivery window on this partner.
                for window in self.delivery_time_window_ids:
                    # Convert the window weekdays from ``time.weekday`` names to ints.
                    weekdays = set(
                        map(int, window.time_window_weekday_ids.mapped("name"))
                    )
                    # Skip windows that do not apply to this candidate weekday.
                    if next_date.weekday() not in weekdays:
                        continue
                    # Get the local time at which this window starts.
                    start_time = window.get_time_window_start_time()
                    # Get the local time at which this window ends.
                    end_time = window.get_time_window_end_time()
                    # Day zero needs special handling because it has a real input time.
                    if not days_to_add:
                        # Date only values only need the day to match the window.
                        if not isinstance(from_date, datetime):
                            return from_datetime
                        # Datetime values inside the window are already valid.
                        elif start_time <= from_datetime_tz_aware.time() <= end_time:
                            return from_datetime
                        # If the candidate time is after this window, try later windows.
                        elif from_datetime_tz_aware.time() > end_time:
                            continue
                    # For future days, or before today's window, choose the start time.
                    next_datetime = next_date.replace(
                        hour=start_time.hour,
                        minute=start_time.minute,
                        second=start_time.second,
                        microsecond=start_time.microsecond,
                    )
                    # Convert partner local window start back to Odoo naive UTC.
                    return next_datetime.astimezone(pytz.utc).replace(tzinfo=None)
        # Any other preference is invalid data.
        else:  # pragma: no cover
            raise ValueError(
                self.env._(
                    "Invalid delivery time preference: %s",
                    self.delivery_time_preference,
                )
            )
        # No matching window was found across the searched week.
        raise UserError(self.env._("No available delivery date found"))
