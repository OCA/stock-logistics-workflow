# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
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
#############################################################################
import logging

from openerp.osv import orm, osv, fields
from openerp.tools.translate import _
from openerp import netsvc
_logger = logging.getLogger(__name__)

class StockPicking(orm.Model):
    _inherit = "stock.picking"
    _columns = {
        'priority': fields.selection([('0', 'Normal'),
                                      ('1', 'Urgent'),
                                      ('2', 'Very Urgent')],
                                     'Priority',
                                     required=True,
                                     help='The priority of the picking'),
        }
    _defaults = {
        'priority': '0',
        }
    def retry_assign_all(self, cr, uid, ids, context=None):
        domain = [('type', '!=', 'in'),
                  ('move_lines', '!=', []),
                  ('state', 'in', ('confirmed', 'assigned'))]
        if ids:
            domain += [('ids', 'in', ids)]
        picking_ids = self.search(cr, uid, domain, order='priority desc, min_date', context=context)
        _logger.info('cancelling pickings')
        cancelled_ids = self.cancel_assign(cr, uid, picking_ids, context)
        assigned_ids = []
        errors = []
        _logger.info('reassigning pickings')
        for picking_id in picking_ids:
            try:
                assigned_id = self.action_assign(cr, uid, [picking_id], context)
                assigned_ids.append(assigned_id)
            except osv.except_osv, exc:
                name = self.read(cr, uid, picking_id, ['name'], context=context)['name']
                errors.append(u'%s: %s' % (name, exc.args[-1]))
                _logger.info('error in action_assign for picking %s: %s' % (name, exc))
        if errors:
            message = '\n'.join(errors)
            raise orm.except_orm(_(u'Warning'),
                                 _(u'No operations validated due to the following errors:\n%s') % message)
        return cancelled_ids, assigned_ids

class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'priority': fields.selection([('0', 'Normal'),
                                      ('1', 'Urgent'),
                                      ('2', 'Very Urgent')],
                                     'Priority',
                                     required=True,
                                     help='The priority of the picking'),
        }
    _defaults = {
        'priority': '0',
        }

    def retry_assign_all(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').retry_assign_all(cr, uid, ids, context=context)

class StockPickingIn(orm.Model):
    _inherit = 'stock.picking.in'
    _columns = {
        'priority': fields.selection([('0', 'Normal'),
                                      ('1', 'Urgent'),
                                      ('2', 'Very Urgent')],
                                     'Priority',
                                     required=True,
                                     help='The priority of the picking'),
        }
    _defaults = {
        'priority': '0',
        }

    def retry_assign_all(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').retry_assign_all(cr, uid, ids, context=context)




class StockPickingRetryAvailability(orm.TransientModel):
    _name = "stock.picking.retry.availability"
    _columns = {
        }

    def action_retry_assign(self, cr, uid, ids, context=None):
        pick_obj = self.pool['stock.picking']

        pick_obj.retry_assign_all(cr, uid, [], context=context)

        return {'type': 'ir.actions.act_window_close'}
