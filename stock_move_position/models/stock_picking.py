# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "line.numbering.mixin"]

    _line_field = "move_ids"
    _line_position_field = "position"

    @api.model_create_multi
    def create(self, vals_list):
        """Sequence the new transfers in their batch and number its moves."""
        next_sequences = {}
        for vals in vals_list:
            if (batch_id := vals.get("batch_id")) and "batch_sequence" not in vals:
                if batch_id not in next_sequences:
                    next_sequences[batch_id] = self._get_next_batch_sequence(batch_id)
                vals["batch_sequence"] = next_sequences[batch_id]
                next_sequences[batch_id] += 1
        pickings = super().create(vals_list)
        # A picking can be attached to an existing batch directly at
        # create() (batch_id set in vals), which never calls
        # stock.picking.batch.write() and so never triggers its
        # batch_position auto-renumbering.
        pickings.batch_id._auto_renumber_lines_positions()
        return pickings

    def write(self, vals):
        """Put the transfers joining a batch last and number its moves."""
        joining, next_sequence = self.browse(), 0
        if (batch_id := vals.get("batch_id")) and "batch_sequence" not in vals:
            # Pickings joining a batch go after the ones already in it, so
            # that the existing batch positions don't move. Pickings that
            # are already in the batch keep their sequence.
            joining = self.filtered(lambda p: p.batch_id.id != batch_id)
            next_sequence = self._get_next_batch_sequence(batch_id)
        res = super().write(vals)
        for sequence, picking in enumerate(joining.sorted("id"), start=next_sequence):
            picking.batch_sequence = sequence
        if "batch_id" in vals:
            # Same as create(): the "Add to batch" wizard attaches
            # pickings to a batch by writing batch_id on the picking,
            # bypassing stock.picking.batch.write().
            self.batch_id._auto_renumber_lines_positions()
        return res

    def _get_next_batch_sequence(self, batch_id):
        """Batch sequence following the last transfer of the batch."""
        batch = self.env["stock.picking.batch"].browse(batch_id)
        return max(batch.picking_ids.mapped("batch_sequence"), default=0) + 1

    def action_renumber_lines_positions(self):
        """Renumber the transfer's moves (UI action)."""
        self.ensure_one()
        return super().renumber_lines_positions()
