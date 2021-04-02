# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.tools.misc import format_datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _planned_delivery_date(self):
        return self.scheduled_date

    @api.onchange("scheduled_date")
    def _onchange_scheduled_date(self):
        self.ensure_one()
        if (
            not self.partner_id
            or self.partner_id.delivery_time_preference != "time_windows"
            or self.picking_type_id.code != "outgoing"
        ):
            return
        p = self.partner_id
        if not p.is_in_delivery_window(self._planned_delivery_date()):
            return {"warning": self._scheduled_date_no_delivery_window_match_msg()}

    def _scheduled_date_no_delivery_window_match_msg(self):
        delivery_windows_strings = []
        for w in self.partner_id.get_delivery_windows().get(self.partner_id.id):
            delivery_windows_strings.append(
                "  * {} ({})".format(w.display_name, self.partner_id.tz)
            )
        message = _(
            "The scheduled date is %s (%s), but the partner is "
            "set to prefer deliveries on following time windows:\n%s"
            % (
                format_datetime(self.env, self.scheduled_date),
                self.env.context.get("tz"),
                "\n".join(delivery_windows_strings),
            )
        )
        return {
            "title": _(
                "Scheduled date does not match partner's Delivery window preference."
            ),
            "message": message,
        }
