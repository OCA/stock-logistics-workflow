# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.tools.misc import format_datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        self.ensure_one()
        if (
            not self.partner_id or
            self.partner_id.delivery_time_preference != 'time_windows' or
            self.picking_type_id.code != 'outgoing'
        ):
            return
        p = self.partner_id
        if not p.is_in_delivery_window(self.scheduled_date):
            return {
                "warning": {
                    "title": _(
                        "Scheduled date does not match partner's Delivery time"
                        " schedule preference."
                    ),
                    "message": _(
                        "The scheduled date is %s, but the partner is "
                        "set to prefer deliveries on following time windows:\n%s"
                        % (
                            format_datetime(self.env, self.scheduled_date),
                            '\n'.join(
                                [
                                    "  * %s" % w.display_name
                                    for w
                                    in p.get_delivery_windows().get(p.id)
                                ]
                            ),
                        )
                    ),
                }
            }
