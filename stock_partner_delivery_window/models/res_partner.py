# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import warnings
from collections import defaultdict
from datetime import datetime, time, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.date_utils import date_range
from odoo.tools.misc import format_time

from odoo.addons.partner_tz.tools import tz_utils

WORKDAYS = list(range(5))


class ResPartner(models.Model):

    _inherit = "res.partner"

    delivery_time_preference = fields.Selection(
        [
            ("anytime", "Any time"),
            ("time_windows", "Fixed time windows"),
            ("workdays", "Weekdays (Monday to Friday)"),
        ],
        string="Delivery time schedule preference",
        default="anytime",
        required=True,
        help="Define the scheduling preference for delivery orders:\n\n"
        "* Any time: Do not postpone deliveries\n"
        "* Fixed time windows: Postpone deliveries to the next preferred "
        "time window\n"
        "* Weekdays: Postpone deliveries to the next weekday",
    )

    delivery_time_window_ids = fields.One2many(
        "partner.delivery.time.window", "partner_id", string="Delivery time windows"
    )

    @api.constrains("delivery_time_preference", "delivery_time_window_ids")
    def _check_delivery_time_preference(self):
        for partner in self:
            if (
                partner.delivery_time_preference == "time_windows"
                and not partner.delivery_time_window_ids
            ):
                raise ValidationError(
                    _(
                        "Please define at least one delivery time window or change"
                        " preference to Any time"
                    )
                )

    def get_delivery_windows(self, day_name=None):
        """
        Return the list of delivery windows by partner id for the given day

        :param day: The day name (see time.weekday, ex: 0,1,2,...)
        :return: dict partner_id: delivery_window recordset
        """
        res = {}
        domain = [("partner_id", "in", self.ids)]
        if day_name is not None:
            week_day_id = self.env["time.weekday"]._get_id_by_name(day_name)
            domain.append(("time_window_weekday_ids", "in", week_day_id))
        windows = self.env["partner.delivery.time.window"].search(domain)
        for window in windows:
            if not res.get(window.partner_id.id):
                res[window.partner_id.id] = self.env[
                    "partner.delivery.time.window"
                ].browse()
            res[window.partner_id.id] |= window
        return res

    def is_in_delivery_window(self, date_time):
        """
        Checks if provided date_time is in a delivery window for actual partner

        :param date_time: Datetime object
        :return: Boolean
        """
        self.ensure_one()
        if self.delivery_time_preference == "anytime":
            return True
        elif self.delivery_time_preference == "workdays":
            if date_time.weekday() > 4:
                return False
            return True
        windows = self.get_delivery_windows(date_time.weekday()).get(self.id)
        if windows:
            for w in windows:
                start_time = w.get_time_window_start_time()
                end_time = w.get_time_window_end_time()
                if self.tz:
                    utc_start = tz_utils.tz_to_utc_time(self.tz, start_time)
                    utc_end = tz_utils.tz_to_utc_time(self.tz, end_time)
                else:
                    utc_start = start_time
                    utc_end = end_time
                if utc_start <= date_time.time() <= utc_end:
                    return True
        return False

    def _get_delivery_time_format_string(self):
        warnings.warn(
            "Method `_get_delivery_time_format_string` will be deprecated in the next version",
            DeprecationWarning,
            stacklevel=2,
        )
        return _("From %(start)s to %(end)s")

    def get_delivery_time_description(self):
        warnings.warn(
            "Method `get_delivery_time_description` will be deprecated in the next version",
            DeprecationWarning,
            stacklevel=2,
        )
        res = dict()
        day_translated_values = dict(
            self.env["time.weekday"]._fields["name"]._description_selection(self.env)
        )

        def short_format_time(time):
            return format_time(self.env, time, time_format="short")

        weekdays = self.env["time.weekday"].search([])
        for partner in self:
            opening_times = defaultdict(list)
            time_format_string = self._get_delivery_time_format_string()
            if partner.delivery_time_preference == "time_windows":
                for day in weekdays:
                    day_windows = partner.delivery_time_window_ids.filtered(
                        lambda d: day in d.time_window_weekday_ids
                    )
                    for win in day_windows:
                        start = win.get_time_window_start_time()
                        end = win.get_time_window_end_time()
                        translated_day = day_translated_values[day.name]
                        value = time_format_string % {
                            "start": short_format_time(start),
                            "end": short_format_time(end),
                        }
                        opening_times[translated_day].append(value)
            elif partner.delivery_time_preference == "workdays":
                day_windows = weekdays.filtered(lambda d: d.name in WORKDAYS)
                for day in day_windows:
                    translated_day = day_translated_values[day.name]
                    value = time_format_string % (
                        short_format_time(time(hour=0, minute=0)),
                        short_format_time(time(hour=23, minute=59)),
                    )
                    opening_times[translated_day].append(value)
            else:
                for day in weekdays:
                    translated_day = day_translated_values[day.name]
                    value = time_format_string % (
                        short_format_time(time(hour=0, minute=0)),
                        short_format_time(time(hour=23, minute=59)),
                    )
                    opening_times[translated_day].append(value)
            opening_times_description = list()
            for day_name, time_list in opening_times.items():
                opening_times_description.append(f"{day_name}: {', '.join(time_list)}")
            res[partner.id] = "\n".join(opening_times_description)
        return res

    def copy_data(self, default=None):
        result = super().copy_data(default=default)[0]
        not_time_windows = self.delivery_time_preference != "time_windows"
        not_copy_windows = not_time_windows or "delivery_time_window_ids" in result
        if not_copy_windows:
            return [result]
        values = [
            {
                "time_window_start": window_id.time_window_start,
                "time_window_end": window_id.time_window_end,
                "time_window_weekday_ids": [
                    (4, wd_id.id, 0) for wd_id in window_id.time_window_weekday_ids
                ],
            }
            for window_id in self.delivery_time_window_ids
        ]
        result["delivery_time_window_ids"] = [(0, 0, val) for val in values]
        return [result]

    def next_delivery_window_start_datetime(self, from_date=None, timedelta_days=None):
        """Get next starting datetime in a preferred delivery window.

        If from_date is already in a delivery window, from_date is "the next"

        :param from_date: Datetime object (Leave empty to use now())
        :param timedelta_days: Number of days to use in the computation
                               (Leave empty to use 7 days or 1 week)
        :return: Datetime object
        """
        self.ensure_one()
        from_date = from_date or datetime.now()
        if self.is_in_delivery_window(from_date):
            return fields.Datetime.to_datetime(from_date)
        if timedelta_days is None:
            timedelta_days = 7
        if self.delivery_time_preference == "workdays":
            datetime_windows = self.get_next_workdays_datetime(
                from_date, from_date + timedelta(days=timedelta_days)
            )
        else:
            datetime_windows = self.get_next_windows_start_datetime(
                from_date, from_date + timedelta(days=timedelta_days)
            )
        for dwin_start in datetime_windows:
            if dwin_start >= from_date:
                return dwin_start
        raise UserError(
            _("Something went wrong trying to find next delivery window. Date: %s")
            % str(from_date)
        )

    def get_next_workdays_datetime(self, from_datetime, to_datetime):
        """Returns all the delivery windows in the provided date range.

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        :return: List of Datetime objects
        """
        dates = date_range(from_datetime, to_datetime, timedelta(days=1))
        return [date for date in dates if date.weekday() < 5]

    def get_next_windows_start_datetime(self, from_datetime, to_datetime):
        """Get all delivery windows start time.

        Range from from_datetime weekday to to_datetime weekday.

        Note result can include a start datetime that is before from_datetime
        on the from_datetime weekday

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        :return: List of Datetime objects
        """
        res = list()
        dts = date_range(from_datetime, to_datetime, timedelta(days=1))
        weekdays = {
            x.name: x for x in self.env["time.weekday"].search([("name", "in", dts)])
        }
        for this_datetime, this_weekday in weekdays.items():
            # Sort by start time to ensure the window we'll find will be the first
            # one for the weekday
            this_weekday_windows = self.delivery_time_window_ids.filtered(
                lambda w: this_weekday in w.time_window_weekday_ids
            ).sorted("time_window_start")
            for win in this_weekday_windows:
                this_weekday_start_datetime = datetime.combine(
                    this_datetime, win.get_time_window_start_time()
                )
                res.append(this_weekday_start_datetime)
        return res

    # TODO: Refactor with function above
    def get_next_delivery_availability(self, from_datetime, to_datetime=None):
        """Get all delivery windows start time.

        Range from from_datetime weekday to to_datetime weekday.

        Note result can include a start datetime that is before from_datetime
        on the from_datetime weekday

        :param from_datetime: Datetime object
        :param to_datetime: Datetime object
        """
        self.ensure_one()
        if to_datetime is None:
            to_datetime = from_datetime + timedelta(days=365)
        for this_datetime in date_range(from_datetime, to_datetime, timedelta(days=1)):
            if self.delivery_time_preference == "anytime":
                yield this_datetime
            else:
                this_weekday_number = this_datetime.weekday()
                if self.delivery_time_preference == "workdays":
                    if this_weekday_number < 5:
                        yield this_datetime
                else:
                    this_weekday_windows = self.env[
                        "partner.delivery.time.window"
                    ].search(
                        [
                            ("time_window_weekday_ids.name", "=", this_weekday_number),
                            ("partner_id", "=", self.id),
                        ],
                        order="time_window_start ASC",
                    )
                    for win in this_weekday_windows:
                        this_weekday_start_datetime = datetime.combine(
                            this_datetime, win.get_time_window_start_time()
                        )
                        yield this_weekday_start_datetime
