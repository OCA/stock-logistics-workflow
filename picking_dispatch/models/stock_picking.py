# -*- coding: utf-8 -*-
# @2016 Cyril Gaudin, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    def _get_related_dispatch(self, cr, uid, ids, field_names, arg=None,
                              context=None):
        result = {}
        if not ids:
            return result
        for pick_id in ids:
            result[pick_id] = []
        sql = ("SELECT DISTINCT sm.picking_id, sm.dispatch_id "
               "FROM stock_move sm "
               "WHERE sm.picking_id in %s AND sm.dispatch_id is NOT NULL")
        cr.execute(sql, (tuple(ids),))
        res = cr.fetchall()
        for picking_id, dispatch_id in res:
            result[picking_id].append(dispatch_id)
        return result

    def _search_dispatch_pickings(self, cr, uid, obj, name, args,
                                  context=None):
        if not len(args):
            return []
        picking_ids = set()
        for field, symbol, value in args:
            move_obj = self.pool['stock.move']
            move_ids = move_obj.search(cr, uid,
                                       [('dispatch_id', symbol, value)],
                                       context=context)
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                picking_ids.add(move.picking_id.id)
        return [('id', 'in', list(picking_ids))]

    _columns = {
        'related_dispatch_ids': fields.function(
            _get_related_dispatch, fnct_search=_search_dispatch_pickings,
            type='one2many', relation='picking.dispatch',
            string='Related Dispatch Picking'),
    }
