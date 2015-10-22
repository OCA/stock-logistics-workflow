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

    def get_packs(self):
        pack_line_model = self.env['stock.picking.package.preparation.line']
        pack_lines = pack_line_model.search([
            ('move_id', '=', self.id),
            ])
        return pack_lines.mapped('package.preparation_id')

    @api.multi
    def write(self, values):
        res = super(StockMove, self).write(values)
        if not self.env.context.get('skip_update_line_ids', False):
            pack_to_update = self.env['stock.picking.package.preparation']
            for move in self:
                pack_to_update |= move.get_packs()
            if pack_to_update:
                pack_to_update._update_line_ids()
        return res

    @api.multi
    def unlink(self):
        pack_to_update = self.env['stock.picking.package.preparation']
        for move in self:
            pack_to_update |= move.get_packs()
        res = super(StockMove, self).unlink()
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res
