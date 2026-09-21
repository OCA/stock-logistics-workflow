# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    putaway_pending = fields.Boolean(
        compute="_compute_putaway_pending",
        help="Technical field: True if deferred putaway has not yet been applied on all lines.",
    )

    @api.depends("move_line_ids.putaway_deferred")
    def _compute_putaway_pending(self):
        for picking in self:
            picking.putaway_pending = any(
                picking.move_line_ids.mapped("putaway_deferred")
            )

    def _can_recompute_putaway(self):
        self.ensure_one()
        if self.picking_type_id.defer_putaway_to_operator:
            # For deferred pickings, skip the `not printed` check: the operator
            # must be able to apply putaway regardless of print state.
            return (
                self.state == "assigned" and self.putaway_pending
            ) or super()._can_recompute_putaway()
        return super()._can_recompute_putaway()

    @api.depends(
        "picking_type_id.defer_putaway_to_operator",
        "move_line_ids.putaway_deferred",
    )
    def _compute_can_recompute_putaways(self):
        return super()._compute_can_recompute_putaways()
