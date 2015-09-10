# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Lorenzo Battistini - Agile Business Group
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
##############################################################################

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def write(self, values):
        res = super(StockMove, self).write(values)
        if 'product_uom_qty' in values:
            for move in self:
                prep_line_model = self.env[
                    'stock.picking.package.preparation.line'
                    ]
                prep_lines = prep_line_model.search([
                    ('move_id', '=', move.id),
                    ])
                prep_lines.product_uom_qty = values['product_uom_qty']
        return res
