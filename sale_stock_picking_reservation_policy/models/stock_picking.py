# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends("move_ids.sale_line_id")
    def _compute_reservation_policy(self):  # pylint: disable=missing-return
        # Transfers generated from a sale order take their policy from the
        # order instead of the operation type. Mirrors how sale_stock overrides
        # the picking's shipping policy (move_type) to follow the sale order's
        # picking_policy.
        super()._compute_reservation_policy()
        for picking in self:
            if sale_orders := picking.move_ids.sale_line_id.order_id:
                # All-or-nothing per line wins when several orders share one
                # transfer.
                picking.reservation_policy = (
                    "line"
                    if any(so.reservation_policy == "line" for so in sale_orders)
                    else "direct"
                )
