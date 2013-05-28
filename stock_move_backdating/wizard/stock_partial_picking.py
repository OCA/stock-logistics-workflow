# -*- coding: utf-8 -*-
from osv import fields, osv
from datetime import datetime

class stock_partial_picking_line(osv.TransientModel):
    _inherit = 'stock.partial.picking.line'
    _name = "stock.partial.picking.line"
    _columns = {
        'date_backdating': fields.datetime("Actual Movement Date"),
    }

    def on_change_date_backdating(self, cr, uid, ids, date_backdating, context=None):
         move_obj = self.pool.get('stock.move')
         return move_obj.on_change_date_backdating(cr, uid, ids, date_backdating, context=context)


class stock_partial_picking(osv.osv_memory):
    _inherit = 'stock.partial.picking'
    name = 'stock.partial.picking'

    def _partial_move_for(self, cr, uid, move):
        partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        partial_move.update({'date_backdating': move.date_backdating},)
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        import pdb; pdb.set_trace()
        partial = self.browse(cr, uid, ids[0], context=context)
        for wizard_line in partial.move_ids:
            date_backdating = wizard_line.date_backdating
            wizard_line.move_id.write({'date_backdating': date_backdating,})
        return super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)



