# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime
import pytz

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.partner_tz.tools import tz_utils


class DeliveryTimeWindow(models.Model):

    _name = "partner.delivery.time.window"
    _inherit = "time.window.mixin"
    _description = "Preferred delivery time windows"

    _overlap_check_field = 'partner_id'

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )
    tz = fields.Selection(
        _tz_get, related="partner_id.tz", readonly=True,
    )
    tz_display_name = fields.Char(compute="_compute_tz_display_name")

    @api.depends("start", "end", "weekday_ids", "tz")
    def _compute_tz_display_name(self):
        for record in self:
            start_time = tz_utils.tz_to_tz_time(
                record.tz, self.env.user.tz, record.get_start_time()
            )
            end_time = tz_utils.tz_to_tz_time(
                record.tz, self.env.user.tz, record.get_end_time()
            )
            record.tz_display_name = _("{days}: From {start} to {end}").format(
                days=", ".join(record.weekday_ids.mapped("display_name")),
                start="%02d:%02d" % (start_time.hour, start_time.minute),
                end="%02d:%02d" % (end_time.hour, end_time.minute),
            )

    @api.constrains("partner_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()

    @api.model
    def float_to_time(self, value):
        # TODO Move to base_time_window?
        res = super().float_to_time(value)
        if self.tz and self.tz != 'UTC':
            # Convert here to naive datetime in UTC
            tz_loc = pytz.timezone(self.tz)
            utc_loc = pytz.timezone('UTC')
            tz_now = datetime.now().astimezone(tz_loc)
            tz_res = datetime.combine(tz_now, res)
            res = tz_loc.localize(tz_res).astimezone(utc_loc).replace(tzinfo=None).time()
        return res
