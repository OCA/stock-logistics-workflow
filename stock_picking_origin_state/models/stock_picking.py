# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    origin_state = fields.Selection(
        selection=[
            ("waiting", "Waiting"),
            ("partially_available", "Partially Available"),
            ("assigned", "Ready"),
            ("done", "Done"),
        ],
        compute="_compute_origin_state",
        help=(
            "Aggregated state of the origin pickings. Reports the deepest "
            "level still active; once every origin picking is done, "
            "reports the closest origin as Done. Empty only when the "
            "picking has no origin pickings."
        ),
    )
    origin_state_label = fields.Char(
        compute="_compute_origin_state",
        help="Display string combining Origin Operation Type and Origin State",
    )

    @api.depends(
        "move_ids.move_orig_ids.state",
        "move_ids.move_orig_ids.picking_id.state",
        "move_ids.move_orig_ids.picking_id.move_ids.state",
    )
    def _compute_origin_state(self):
        state_labels = dict(
            self._fields["origin_state"]._description_selection(self.env)
        )
        for picking in self:
            origin_pickings, state = picking._get_origin_level()
            if not origin_pickings:
                picking.origin_state = False
                picking.origin_state_label = False
                continue
            picking_type = origin_pickings[:1].picking_type_id
            picking.origin_state = state
            type_name = self._get_origin_state_label_type_name(picking_type)
            state_label = state_labels.get(state, "")
            picking.origin_state_label = (
                f"{type_name}: {state_label}" if type_name else state_label
            )

    def _get_origin_state_label_type_name(self, picking_type):
        return picking_type.display_name or ""

    def _get_origin_level(self):
        """
        Return the deepest origin level still active
        """
        self.ensure_one()
        Picking = self.env["stock.picking"]
        levels = []
        seen_ids = set(self.ids)
        frontier = self
        while True:
            picking_orig_ids = frontier.mapped("move_ids.move_orig_ids.picking_id")
            picking_orig_ids = picking_orig_ids.filtered(lambda p: p.id not in seen_ids)
            if not picking_orig_ids:
                break
            seen_ids.update(picking_orig_ids.ids)
            levels.append(picking_orig_ids)
            frontier = picking_orig_ids
        for origin_pickings in reversed(levels):
            active_pickings = origin_pickings.filtered(
                lambda p: p.state not in ("done", "cancel")
            )
            if active_pickings:
                return active_pickings, active_pickings._aggregate_origin_state()
        if not levels:
            return Picking, None
        done_pickings = levels[0].filtered(lambda p: p.state == "done")
        if done_pickings:
            return done_pickings, "done"
        return Picking, None

    def _aggregate_origin_state(self):
        """
        Find the least advanced state among all non-cancelled moves.
        """
        move_state_order = [
            s[0] for s in self.env["stock.move"]._fields["state"].selection
        ]
        moves = self.move_ids.filtered(lambda m: m.state != "cancel")
        if not moves:
            return "waiting"
        worst = min(
            moves.mapped("state"),
            key=lambda s: move_state_order.index(s),
        )
        if worst in ("draft", "waiting", "confirmed"):
            return "waiting"
        if worst == "partially_available":
            return "partially_available"
        return "assigned"
