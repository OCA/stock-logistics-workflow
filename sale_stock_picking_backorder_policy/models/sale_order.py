# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_picking_backorder_policy.models.res_partner import (
    BACKORDER_POLICY_HELP,
    BACKORDER_POLICY_SELECTION,
)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        compute="_compute_backorder_policy",
        store=True,
        readonly=False,
        copy=False,
        help=BACKORDER_POLICY_HELP,
    )

    @api.depends("partner_shipping_id")
    def _compute_backorder_policy(self):
        for order in self:
            order.backorder_policy = order.partner_shipping_id.backorder_policy
