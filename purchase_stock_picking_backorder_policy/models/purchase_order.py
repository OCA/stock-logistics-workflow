# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_picking_backorder_policy.models.stock_picking import (
    BACKORDER_POLICY_HELP,
    BACKORDER_POLICY_SELECTION,
)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        compute="_compute_backorder_policy",
        store=True,
        readonly=False,
        copy=False,
        tracking=True,
        help=BACKORDER_POLICY_HELP,
    )

    @api.depends("partner_id")
    def _compute_backorder_policy(self):
        for order in self:
            order.backorder_policy = order.partner_id.purchase_backorder_policy

    def _prepare_picking(self):
        # Carry the policy onto the receipt created for this order. Purchase
        # creates that receipt itself, so the moves cannot propagate it (see
        # stock.move._get_new_picking_values).
        vals = super()._prepare_picking()
        vals["backorder_policy"] = self.backorder_policy
        return vals
