# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from osv import fields, osv


class stock_partial_picking_line(osv.TransientModel):
    _inherit = 'stock.partial.picking.line'
    _name = "stock.partial.picking.line"
    _columns = {
        'date_backdating': fields.datetime("Actual Movement Date"),
    }

    def on_change_date_backdating(self, cr, uid, ids, date_backdating,
                                  context=None):
        move_obj = self.pool.get('stock.move')
        return move_obj.on_change_date_backdating(
            cr, uid, ids, date_backdating, context=context)


class stock_partial_picking(osv.TransientModel):
    _inherit = 'stock.partial.picking'
    name = 'stock.partial.picking'

    def _partial_move_for(self, cr, uid, move):
        partial_move = super(
            stock_partial_picking, self)._partial_move_for(cr, uid, move)
        partial_move.update({'date_backdating': move.date_backdating},)
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        partial = self.browse(cr, uid, ids[0], context=context)
        for wizard_line in partial.move_ids:
            date_backdating = wizard_line.date_backdating
            wizard_line.move_id.write({'date_backdating': date_backdating, })
        return super(stock_partial_picking, self).do_partial(cr, uid, ids,
                                                             context=context)
