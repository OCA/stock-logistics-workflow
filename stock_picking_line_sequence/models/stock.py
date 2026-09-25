# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # re-defines the field to change the default
    sequence = fields.Integer("HiddenSequence", default=9999)

    # displays sequence on the stock moves
    sequence2 = fields.Integer(
        "Sequence",
        help="Shows the sequence in the Stock Move.",
        related="sequence",
        readonly=True,
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        # We do not reset the sequence if we are copying a complete picking
        # or creating a backorder
        if not self.env.context.get("keep_line_sequence", False):
            moves.picking_id._reset_sequence()
        return moves


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super(
            StockMoveLine, self
        )._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            line_key = self._get_aggregated_properties(move_line=move_line)["line_key"]
            sequence2 = move_line.move_id.sequence2
            if line_key in aggregated_move_lines:
                aggregated_move_lines[line_key]["sequence2"] = sequence2

        return aggregated_move_lines


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends("move_ids_without_package")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in move lines.
        Then we add 1 to this value for the next sequence, this value is
        passed to the context of the o2m field in the view.
        So when we create new move line, the sequence is automatically
        incremented by 1. (max_sequence + 1)
        """
        for picking in self:
            picking.max_line_sequence = (
                max(picking.mapped("move_ids_without_package.sequence") or [0]) + 1
            )

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence"
    )

    def _reset_sequence(self):
        """Number the moves 1, 2, 3... in their (sequence, id) order and only
        write the numbers that change."""
        for rec in self:
            # Skip virtual records, they have no id to sort by yet
            moves = rec.move_ids_without_package.filtered(
                lambda m: isinstance(m.id, int)
            )
            sorted_moves = moves.sorted(lambda m: (m.sequence, m.id))
            for sequence, move in enumerate(sorted_moves, start=1):
                if move.sequence != sequence:
                    move.sequence = sequence

    def copy(self, default=None):
        return super(StockPicking, self.with_context(keep_line_sequence=True)).copy(
            default
        )

    def button_validate(self):
        return super(
            StockPicking, self.with_context(keep_line_sequence=True)
        ).button_validate()
