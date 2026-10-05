# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    putaway_deferred = fields.Boolean(
        default=False,
        copy=False,
        help=(
            "Putaway strategy has not been applied for this operation. "
            "Use 'Recompute Putaways' on the picking before validating."
        ),
    )

    @api.depends(
        "picking_type_id.defer_putaway_to_operator",
        "putaway_deferred",
    )
    def _compute_can_recompute_putaways(self):
        return super()._compute_can_recompute_putaways()

    def write(self, vals):
        to_clear = self.env["stock.move.line"]
        if (
            "location_dest_id" in vals
            and not self.env.context.get("deferred_putaway_apply")
            and not self.env.context.get("in_action_assign")
        ):
            to_clear = self.filtered("putaway_deferred")
        if to_clear == self:
            # If the operator has manually set a destination on a deferred line,
            # it is no longer deferred.
            vals["putaway_deferred"] = False
        result = super().write(vals)
        if to_clear and to_clear != self:
            to_clear.putaway_deferred = False
        return result

    def _can_recompute_putaway(self):
        # Allow recomputation for package-level moves (whole package being
        # relocated): result_package_id == package_id in that case, and the
        # package_level_id is always set.  Only exclude lines whose
        # result_package_id represents a *new* package being filled during the
        # operation (no package_level_id), since the operator has explicitly
        # chosen that destination and it must never be overridden.
        if self.picking_type_id.defer_putaway_to_operator:
            return self.picking_id._can_recompute_putaway() and not (
                self.result_package_id and self.result_package_id != self.package_id
            )
        return super()._can_recompute_putaway()

    def _apply_putaway_strategy(self):
        if not self._context.get("deferred_putaway_apply"):
            # Lines belonging to deferred picking types must not have their
            # putaway computed now (called from _action_assign). Mark them and
            # leave their location_dest_id at the move's destination.
            # Lines whose result_package_id is a *new* package being filled
            # (no package_level_id) are excluded: the operator sets that
            # destination explicitly and it cannot be recomputed.  Lines that
            # move a whole existing package (package_level_id is set) are
            # included in the deferred mechanism.
            deferred = self.filtered(
                lambda line: line.picking_type_id.defer_putaway_to_operator
                and not (
                    line.result_package_id and self.result_package_id != self.package_id
                )
            )
            if deferred:
                deferred.putaway_deferred = True
            return super(StockMoveLine, self - deferred)._apply_putaway_strategy()
        return super()._apply_putaway_strategy()

    def _action_done(self):
        deferred = self.filtered("putaway_deferred")
        if deferred:
            raise UserError(
                _(
                    "Putaway strategy has not been applied on the following operations:\n%s\n"
                    "Use 'Recompute Putaways' before processing.",
                    "\n".join(
                        f"- {line.product_id.display_name} -> "
                        f"{line.location_dest_id.display_name}"
                        for line in deferred
                    ),
                )
            )
        return super()._action_done()

    def _recompute_putaways(self) -> None:
        to_recompute_lines = self._filtered_for_putaway_recompute()
        # Inject context so that _apply_putaway_strategy (called inside super)
        # does not skip deferred lines this time.
        res = super(
            StockMoveLine, to_recompute_lines.with_context(deferred_putaway_apply=True)
        )._recompute_putaways()
        to_recompute_lines.putaway_deferred = False
        return res
