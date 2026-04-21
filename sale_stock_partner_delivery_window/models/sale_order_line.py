# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _expected_date(self):
        # OVERRIDE to account for the partner's delivery schedule preference
        # The original method, called with `super()`, returns the earliest deliverable
        # date based on our customer lead time.
        # We want to pick up on that and compare against the partner's delivery schedule
        # preference. If it doesn't match, we will postpone the expected date to the
        # next available time window.
        expected_date = super()._expected_date()
        partner = self.order_id.partner_id
        return partner._next_available_delivery_date(expected_date)

    @api.depends("order_id.partner_id")
    def _compute_qty_at_date(self):
        # OVERRIDE to add the `partner_id` to the dependencies
        return super()._compute_qty_at_date()
