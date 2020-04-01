# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime
import pytz

from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get


class DeliveryTimeWindow(models.Model):

    _name = "partner.delivery.time.window"
    _inherit = "time.window.mixin"
    _description = "Preferred delivery time windows"

    _overlap_check_field = 'partner_id'

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )
    # TODO Move to base_time_window?
    tz = fields.Selection(
        _tz_get, string='Timezone', default=lambda p: p.env.user.company_id.partner_id.tz
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
