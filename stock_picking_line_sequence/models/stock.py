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

    @api.model
    def create(self, values):
        move = super(StockMove, self).create(values)
        # We do not reset the sequence if we are copying a complete picking
        # or creating a backorder
        if not self.env.context.get("keep_line_sequence", False):
            move.picking_id._reset_sequence()
        return move


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
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

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.move_ids_without_package:
                line.sequence = current_sequence
                current_sequence += 1

    @api.multi
    def copy(self, default=None):
        return super(StockPicking, self.with_context(keep_line_sequence=True)).copy(
            default
        )

    @api.multi
    def button_validate(self):
        return super(
            StockPicking, self.with_context(keep_line_sequence=True)
        ).button_validate()
