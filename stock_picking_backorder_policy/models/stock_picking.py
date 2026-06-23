# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .res_partner import BACKORDER_POLICY_HELP, BACKORDER_POLICY_SELECTION


class StockPicking(models.Model):
    _inherit = "stock.picking"

    backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        compute="_compute_backorder_policy",
        store=True,
        readonly=False,
        help=BACKORDER_POLICY_HELP,
    )

    @api.depends("partner_id")
    def _compute_backorder_policy(self):
        # Default to the delivery partner's policy. This covers transfers
        # created directly, e.g. from the Inventory app. Transfers generated
        # from a sale order have their policy propagated through the moves
        # instead (see stock.move._get_new_picking_values), which overrides
        # this default.
        for picking in self:
            picking.backorder_policy = picking.partner_id.backorder_policy

    def _check_backorder(self):
        # Skip the backorder wizard for pickings with a deterministic policy.
        # 'always'/'never' are resolved without prompting (see _action_done);
        # 'ask' (or no policy) falls back to the standard behavior.
        pickings = self.filtered(
            lambda p: p.backorder_policy not in ("always", "never")
        )
        return super(StockPicking, pickings)._check_backorder()

    def _action_done(self):
        # Enforce the backorder policy through the core `cancel_backorder`
        # context flag (the same one the backorder confirmation wizard uses):
        #   - never  -> cancel the remaining demand, no backorder
        #   - always -> create the backorder
        #   - ask / unset -> keep the incoming behavior (operation type default)
        validated_ids = self.env.context.get("button_validate_picking_ids") or []
        validated = self.filtered(lambda p: p.id in validated_ids)
        if never := validated.filtered(lambda p: p.backorder_policy == "never"):
            never = never.with_context(cancel_backorder=True)
            super(StockPicking, never)._action_done()
        if always := validated.filtered(lambda p: p.backorder_policy == "always"):
            always = always.with_context(cancel_backorder=False)
            super(StockPicking, always)._action_done()
        if rest := (self - never - always):
            super(StockPicking, rest)._action_done()
        return True
