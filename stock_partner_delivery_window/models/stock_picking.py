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
        partner = self.partner_id
        anytime_delivery = partner and partner.delivery_time_preference == "anytime"
        outgoing_picking = self.picking_type_id.code == "outgoing_picking"
        # Return nothing if partner delivery preference is anytime
        if not partner or anytime_delivery or outgoing_picking:
            return
        if not partner.is_in_delivery_window(self._planned_delivery_date()):
            return {"warning": self._scheduled_date_no_delivery_window_match_msg()}

    def _scheduled_date_no_delivery_window_match_msg(self):
        scheduled_date = self.scheduled_date
        formatted_scheduled_date = format_datetime(self.env, scheduled_date)
        partner = self.partner_id
        if partner.delivery_time_preference == "workdays":
            message = _(
                "The scheduled date is {} ({}), but the partner is "
                "set to prefer deliveries on working days."
            ).format(formatted_scheduled_date, scheduled_date.weekday())
        else:
            delivery_windows_strings = []
            for w in partner.get_delivery_windows().get(partner.id):
                delivery_windows_strings.append(
                    "  * {} ({})".format(w.display_name, partner.tz)
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
