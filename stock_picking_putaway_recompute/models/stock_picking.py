# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing_extensions import Self

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    can_recompute_putaways = fields.Boolean(
        compute="_compute_can_recompute_putaways",
        help="Technical field in order to display the Recompute Putaways button.",
    )

    def action_recompute_putaways(self) -> dict:
        """
        Launches the putaways recomputation on operations
        """
        for picking in self:
            picking.move_line_ids._recompute_putaways()

    def _can_recompute_putaway(self):
        self.ensure_one()
        return (
            self.picking_type_id.allow_to_recompute_putaways
            and self.state == "assigned"
            and not self.printed
        )

    def _filtered_can_recompute_putaways(self) -> Self:
        """
        Filter current recordset in order to get the pickings that can
        """
        return self.filtered(lambda pick: pick._can_recompute_putaway())

    @api.depends("picking_type_id.allow_to_recompute_putaways", "state", "printed")
    def _compute_can_recompute_putaways(self):
        can_recompute_pickings = self._filtered_can_recompute_putaways()
        can_recompute_pickings.can_recompute_putaways = True
        (self - can_recompute_pickings).can_recompute_putaways = False
