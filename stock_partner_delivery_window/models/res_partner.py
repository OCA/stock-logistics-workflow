# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_time

from odoo.addons.partner_tz.tools import tz_utils


class ResPartner(models.Model):

    _inherit = "res.partner"

    delivery_time_preference = fields.Selection(
        [("anytime", "Any time"), ("time_windows", "Fixed time windows")],
        string="Delivery time schedule preference",
        default="anytime",
        required=True,
        help="Define the scheduling preference for delivery orders:\n\n"
        "* Any time: Do not postpone deliveries\n"
        "* Fixed time windows: Postpone deliveries to the next preferred "
        "time window",
    )

    delivery_time_window_ids = fields.One2many(
        "partner.delivery.time.window", "partner_id", string="Delivery time windows",
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
                if utc_start <= date_time.time() < utc_end:
                    return True
        return False

    def _get_delivery_time_format_string(self):
        return _("From %s to %s")

    def get_delivery_time_description(self):
        res = dict()
        day_translated_values = dict(
            self.env["time.weekday"]._fields["name"]._description_selection(self.env)
        )
        for partner in self:
            opening_times = {}
            time_format_string = self._get_delivery_time_format_string()
            if partner.delivery_time_preference == "time_windows":
                for day in self.env["time.weekday"].search([]):
                    day_windows = partner.delivery_time_window_ids.filtered(
                        lambda d: day in d.time_window_weekday_ids
                    )
                    for win in day_windows:
                        opening_times.setdefault(day_translated_values[day.name], [])
                        opening_times[day_translated_values[day.name]].append(
                            time_format_string
                            % (
                                format_time(
                                    self.env,
                                    win.get_time_window_start_time(),
                                    time_format="short",
                                ),
                                format_time(
                                    self.env,
                                    win.get_time_window_end_time(),
                                    time_format="short",
                                ),
                            )
                        )
            else:
                for day in self.env["time.weekday"].search([]):
                    opening_times.setdefault(day_translated_values[day.name], [])
                    opening_times[day_translated_values[day.name]].append(
                        time_format_string
                        % (
                            format_time(
                                self.env, time(hour=0, minute=0), time_format="short"
                            ),
                            format_time(
                                self.env, time(hour=23, minute=59), time_format="short"
                            ),
                        )
                    )
            opening_times_description = list()
            for day_name, time_list in opening_times.items():
                opening_times_description.append(
                    _("%s: %s") % (day_name, _(", ").join(time_list))
                )
            res[partner.id] = "\n".join(opening_times_description)
        return res
