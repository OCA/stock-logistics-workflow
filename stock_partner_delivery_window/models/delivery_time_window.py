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

    _time_window_overlap_check_field = 'partner_id'

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )
    tz = fields.Selection(
        _tz_get, related="partner_id.tz", readonly=True,
    )

    @api.constrains("partner_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()

    @api.model
    def float_to_time(self, value):
        # TODO Move to base_time_window?
        res = super().float_to_time(value)
        if self.tz and self.tz != 'UTC':
            # Convert here to time in UTC
            res = tz_utils.tz_to_utc_time(self.tz, res)
        return res
