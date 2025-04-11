# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools.misc import format_datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"
    partner_delivery_window_warning = fields.Text(
        compute="_compute_partner_delivery_window_warning"
    )

    def _planned_delivery_date(self):
        return self.scheduled_date

    @api.depends("partner_id", "scheduled_date")
    def _compute_partner_delivery_window_warning(self):
        for picking in self:
            partner = picking.partner_id
            picking.partner_delivery_window_warning = False
            if not partner:
                continue

            anytime_delivery = partner and partner.delivery_time_preference == "anytime"
            not_outgoing_picking = picking.picking_type_id.code != "outgoing"

            if anytime_delivery or not_outgoing_picking:
                continue

            elif not partner.is_in_delivery_window(self._planned_delivery_date()):
                self.partner_delivery_window_warning = (
                    self._scheduled_date_no_delivery_window_match_msg()
                )

    def _scheduled_date_no_delivery_window_match_msg(self):
        scheduled_date = self.scheduled_date
        formatted_scheduled_date = format_datetime(self.env, scheduled_date)
        partner = self.partner_id
        if partner.delivery_time_preference == "workdays":
            message = self.env._(
                "The scheduled date is %(date)s %(weekday)s, but the partner is "
                "set to prefer deliveries on working days.",
                date=formatted_scheduled_date,
                weekday=scheduled_date.weekday(),
            )
        else:
            delivery_windows_strings = []
            if partner:
                for w in partner.get_delivery_windows().get(partner.id):
                    delivery_windows_strings.append(
                        f"  * {w.display_name} ({partner.tz})"
                    )
            message = self.env._(
                "The scheduled date is %(date)s (%(tz)s), but the partner is "
                "set to prefer deliveries on following time windows:\n%(window)s",
                date=format_datetime(self.env, self.scheduled_date),
                tz=self.env.context.get("tz"),
                window="\n".join(delivery_windows_strings),
            )
        return message
