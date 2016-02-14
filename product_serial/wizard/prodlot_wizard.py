# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2010 NaN Projectes de Programari Lliure, S.L.
#                       http://www.NaN-tic.com
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
from openerp.tools.translate import _


class stock_picking_prodlot_selection_wizard(orm.TransientModel):
    _name = 'stock.picking.prodlot.selection'

    _columns = {
        'product_id': fields.many2one(
            'product.product', 'Product', required=True),
        'prefix': fields.char('Prefix', size=256),
        'suffix': fields.char('Suffix', size=256),
        'first_number': fields.char('First Number', size=256, required=True),
        'last_number': fields.char('Last Number', size=256, required=True),
        'create_prodlots': fields.boolean('Create New Serial Numbers'),
    }

    _defaults = {
        'create_prodlots': False,
    }

    def select_or_create_prodlots(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return {}
        if 'active_id' not in context:
            return {}

        prodlot_obj = self.pool['stock.production.lot']
        record = self.browse(cr, uid, ids[0], context)
        prefix = record.prefix or ''
        suffix = record.suffix or ''
        try:
            first_number = int(record.first_number)
        except:
            raise orm.except_orm(_('Invalid First Number'), _(
                "The field 'First Number' should only contain digits."))

        try:
            last_number = int(record.last_number)
        except:
            raise orm.except_orm(_('Invalid Last Number'), _(
                "The field 'Last Number' should only contain digits."))

        if last_number < first_number:
            raise orm.except_orm(_('Invalid Numbers'), _(
                'The First Number must be lower than the Last Number.'))

        if len(record.first_number) != len(record.last_number):
            raise orm.except_orm(_('Invalid Lot Numbers'), _(
                'First and Last Numbers must have the same length.'))

        number_length = len(record.first_number)

        picking_id = context['active_id']
        current_number = first_number
        picking = self.pool['stock.picking'].browse(
            cr, uid, picking_id, context=context)
        company_id = picking.company_id.id
        for move in picking.move_lines:
            if move.prodlot_id or move.product_id != record.product_id:
                continue

            current_lot = '%%s%%0%dd%%s' % number_length % (
                prefix, current_number, suffix)
            if record.create_prodlots:
                # Create new prodlot
                lot_id_on_move = prodlot_obj.create(cr, uid, {
                    'product_id': record.product_id.id,
                    'name': current_lot,
                    'company_id': company_id,
                }, context=context)
            else:
                # Search existing prodlots
                lot_ids = prodlot_obj.search(
                    cr,
                    uid,
                    [('name', '=', current_lot)],
                    limit=1,
                    context=context)
                if not lot_ids:
                    raise orm.except_orm(
                        _('Invalid lot numbers'),
                        _('Production lot %s not found.') % current_lot)

                ctx = context.copy()
                ctx['location_id'] = move.location_id.id
                prodlot = self.pool.get('stock.production.lot').browse(
                    cr, uid, lot_ids[0], ctx)

                if prodlot.product_id != record.product_id:
                    raise orm.except_orm(
                        _('Invalid lot numbers'),
                        _('Production lot %s exists but not for product %s.') %
                        (current_lot, record.product_id.name))

                if prodlot.stock_available < move.product_qty:
                    raise orm.except_orm(
                        _('Invalid lot numbers'),
                        _('Not enough stock available of production lot %s.') %
                        current_lot)
                lot_id_on_move = lot_ids[0]

            self.pool.get('stock.move').write(cr, uid, [move.id], {
                'prodlot_id': lot_id_on_move,
            }, context=context)

            current_number += 1
            if current_number > last_number:
                break

        return True
