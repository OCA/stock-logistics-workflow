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
    visible_sequence = fields.Integer(
        "Sequence",
        help="Shows the sequence in the Stock Move.",
        related="sequence",
        readonly=True,
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """(re)initialize the sequences of the moves within a picking"""
        moves = super().create(vals_list)
        # We do not reset the sequence if we are copying a complete picking
        # or creating a backorder
        if not self.env.context.get("keep_line_sequence"):
            moves.picking_id._reset_sequence()
        return moves
