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
        "picking_type_id.allow_to_recompute_putaways", "picking_id.printed", "qty_done"
    )
    def _compute_can_recompute_putaways(self):
        can_recompute_lines = self._filtered_for_putaway_recompute()
        can_recompute_lines.can_recompute_putaways = True
        (self - can_recompute_lines).can_recompute_putaways = False

    def _filtered_for_putaway_recompute(self) -> Self:
        """
        Recompute putaways on operations that:

            - have their picking type configured for that
            - have their picking not printed (started)
            - have their qty_done field != 0
        """
        return self.filtered(
            lambda line: line.picking_type_id.allow_to_recompute_putaways
            and not line.picking_id.printed
            and not line.result_package_id
            and not line.qty_done
        )

    def _recompute_putaways(self) -> None:
        """
        Launches the computation of putaways on operations that are
        allowed to.
        """
        self._filtered_for_putaway_recompute()._apply_putaway_strategy()

    def action_recompute_putaways(self):
        self._recompute_putaways()
