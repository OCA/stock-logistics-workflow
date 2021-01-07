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


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super(
            StockMoveLine, self
        )._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            name = move_line.product_id.display_name
            description = move_line.move_id.description_picking
            if description == name or description == move_line.product_id.name:
                description = False
            uom = move_line.product_uom_id
            line_key = (
                str(move_line.product_id.id)
                + "_"
                + name
                + (description or "")
                + "uom "
                + str(uom.id)
            )
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
        for rec in self:
            current_sequence = 1
            for line in rec.move_ids_without_package:
                line.sequence = current_sequence
                current_sequence += 1

    def copy(self, default=None):
        return super(StockPicking, self.with_context(keep_line_sequence=True)).copy(
            default
        )

    def button_validate(self):
        return super(
            StockPicking, self.with_context(keep_line_sequence=True)
        ).button_validate()
