# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockPickingBatch(models.Model):
    _name = "stock.picking.batch"
    _inherit = ["stock.picking.batch", "line.numbering.mixin"]

    _line_field = "move_ids"
    _line_position_field = "batch_position"

    def _line_trigger_fields(self):
        """Renumber when transfers are added or removed."""
        # move_ids is computed from picking_ids; it never appears as a
        # write() vals key, so watch the stored field instead.
        return ["picking_ids"]

    def _get_lines_to_renumber(self):
        """Moves grouped per transfer, transfers in batch order."""
        # OVERRIDE: keep each transfer's moves together, transfers in the
        # order shown on the batch. The sort is stable, so the moves of a
        # transfer keep their order.
        return (
            super()
            ._get_lines_to_renumber()
            .sorted(lambda m: (m.picking_id.batch_sequence, m.picking_id.id))
        )

    def action_renumber_lines_positions(self):
        """Renumber the batch's moves (UI action)."""
        self.ensure_one()
        return super().renumber_lines_positions()
