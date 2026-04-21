# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.misc import format_datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("commitment_date")
    def _onchange_commitment_date_delivery_window(self):
        # OVERRIDE: warn if the commitment date doesn't fit the delivery window
        if not self.commitment_date or not self.partner_id.delivery_time_preference:
            return
        next_date = self.partner_id._next_available_delivery_date(self.commitment_date)
        if self.commitment_date != next_date:
            return {
                "warning": {
                    "title": self.env._("Customer delivery preference not met"),
                    "message": self.env._(
                        "The requested date doesn't fit with the customer delivery "
                        "preference. The next available delivery date is "
                        "%(next_date)s.",
                        next_date=format_datetime(self.env, next_date),
                    ),
                }
            }
