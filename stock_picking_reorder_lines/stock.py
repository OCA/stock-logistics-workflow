# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'date_expected desc, sequence, id'

    sequence = fields.Integer()

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(move,
                                                            partner,
                                                            inv_type)
        res['sequence'] = move.sequence
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_lines')
    def _get_max_line_sequence(self):
        for picking in self:
            if picking.move_lines:
                max_line_sequence = max(
                    picking.mapped('move_lines.sequence')) + 10
            else:
                max_line_sequence = 10
            picking.max_line_sequence = max_line_sequence

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_get_max_line_sequence')
