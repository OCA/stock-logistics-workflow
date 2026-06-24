# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_picking_reservation_policy.models.stock_picking_type import (
    RESERVATION_POLICY_HELP,
    RESERVATION_POLICY_SELECTION,
)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reservation_policy = fields.Selection(
        selection=RESERVATION_POLICY_SELECTION,
        compute="_compute_reservation_policy",
        store=True,
        readonly=False,
        required=True,
        precompute=True,
        help=RESERVATION_POLICY_HELP,
    )

    @api.depends("partner_shipping_id")
    def _compute_reservation_policy(self):
        for order in self:
            order.reservation_policy = (
                order.partner_shipping_id.reservation_policy or "direct"
            )
