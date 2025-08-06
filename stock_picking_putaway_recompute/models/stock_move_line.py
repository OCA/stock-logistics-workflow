# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing_extensions import Self

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    can_recompute_putaways = fields.Boolean(
        compute="_compute_can_recompute_putaways",
    )

    @api.depends(
        "picking_type_id.allow_to_recompute_putaways",
        "picking_id.printed",
        "picking_id.state",
        "result_package_id",
        "picked",
    )
    def _compute_can_recompute_putaways(self):
        can_recompute_lines = self._filtered_for_putaway_recompute()
        can_recompute_lines.can_recompute_putaways = True
        (self - can_recompute_lines).can_recompute_putaways = False

    def _can_recompute_putaway(self):
        self.ensure_one()
        return (
            self.picking_id._can_recompute_putaway()
            and not self.result_package_id
            and not self.picked
        )

    def _filtered_for_putaway_recompute(self) -> Self:
        """
        Recompute putaways on operations that:

            - have their picking type configured for that
            - have their picking not printed (started)
            - have their picked field set
        """
        return self.filtered(lambda line: line._can_recompute_putaway())

    def _recompute_putaways(self) -> None:
        """
        Launches the computation of putaways on operations that are
        allowed to.
        """
        to_recompute_lines = self._filtered_for_putaway_recompute()
        # Reset location destinations to their move destination
        # First, protect the field from recomputations as
        # value will be reaffected afterwards.
        with to_recompute_lines.env.protecting(
            ["location_dest_id"], to_recompute_lines
        ):
            for line in to_recompute_lines:
                line.location_dest_id = line.move_id.location_dest_id
        to_recompute_lines._apply_putaway_strategy()

    def action_recompute_putaways(self):
        self._recompute_putaways()
