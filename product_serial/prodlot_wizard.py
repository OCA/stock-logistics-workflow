# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2010 NaN Projectes de Programari Lliure, S.L.
#                       http://www.NaN-tic.com
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

from openerp.osv import orm, fields
from tools.translate import _

def is_integer(value):
    try:
        int(value)
        return True
    except:
        return False

class stock_picking_prodlot_selection_wizard(orm.TransientModel):
    _name = 'stock.picking.prodlot.selection'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'first_lot': fields.char('First Lot Number', size=256),
        'last_lot': fields.char('Last Lot Number', size=256),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return {}

    def action_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return {}
        if not 'active_id' in context:
            return {}

        record = self.browse(cr, uid, ids[0], context)
        first = record.first_lot
        last = record.last_lot
        if len(first) != len(last):
            raise orm.except_orm(_('Invalid lot numbers'), _('First and last lot numbers must have the same length.'))


        first_number = ''
        last_number = ''
        position = -1
        for x in xrange(len(first)):
            if not position and first[x] == last[x]:
                continue
            if not position:
                position = x
            if not is_integer(first[x]) or not is_integer(last[x]):
                raise orm.except_orm(_('Invalid lot numbers'), _('First and last lot numbers differ in non-numeric values.'))
            first_number += first[x]
            last_number += last[x]

        if position >= 0:
            prefix = first[:position-1]
        else:
            prefix = ''

        number_fill = len(first_number)
        first_number = int(first_number)
        last_number = int(last_number)

        if last_number < first_number:
            raise orm.except_orm(_('Invalid lot numbers'), _('First lot number is greater than the last one.'))

        picking_id = context['active_id']
        current_number = first_number
        for move in self.pool.get('stock.picking').browse(cr, uid, picking_id, context).move_lines:
            if move.prodlot_id or move.product_id != record.product_id:
                continue

            current_lot = '%%s%%0%dd' % number_fill % (prefix, current_number)
            lot_ids = self.pool.get('stock.production.lot').search(cr, uid, [('name','=',current_lot)], limit=1, context=context)
            if not lot_ids:
                raise orm.except_orm(_('Invalid lot numbers'), _('Production lot %s not found.') % current_lot)

            ctx = context.copy()
            ctx['location_id'] = move.location_id.id
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, lot_ids[0], ctx)

            if prodlot.product_id != record.product_id:
                raise orm.except_orm(_('Invalid lot numbers'), _('Production lot %s exists but not for product %s.') % (current_lot, record.product_id.name))

            if prodlot.stock_available < move.product_qty:
                raise orm.except_orm(_('Invalid lot numbers'), _('Not enough stock available of production lot %s.') % current_lot)

            self.pool.get('stock.move').write(cr, uid, [move.id], {
                'prodlot_id': lot_ids[0],
            }, context)

            current_number += 1
            if current_number > last_number:
                break

        return {}


