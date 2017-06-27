# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sequence = fields.Integer(default=9999)
    sequence2 = fields.Integer(help="Shows the sequence in the Stock Move.",
                               related='sequence', readonly=True)

    @api.model
    def create(self, values):
        move = super(StockMove, self).create(values)
        # We do not reset the sequence if we are copying a complete stock move
        if 'keep_line_sequence' not in self.env.context:
            move.picking_id._reset_sequence()
        return move

    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        if 'keep_line_sequence' not in self.env.context:
            default['sequence'] = 9999
        return super(StockMove, self).copy(default)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_lines')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence
        entered in move lines.
        Then we add 1 to this value for the next sequence
        This value is given to the context of the o2m field
        in the view. So when we create new move line,
        the sequence is automatically incremented by 1.
        (max_sequence + 1)
        """
        for picking in self:
            picking.max_line_sequence = (
                max(picking.mapped('move_lines.sequence') or [0]) + 1
                )

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.move_lines:
                line.write({'sequence': current_sequence})
                current_sequence += 1

    @api.multi
    def write(self, values):
        res = super(StockPicking, self).write(values)
        for rec in self:
            rec._reset_sequence()
        return res

    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        return super(StockPicking,
                     self.with_context(keep_line_sequence=True)).copy(default)
