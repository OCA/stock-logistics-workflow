# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm
from openerp.tools.translate import _


class picking_dispatch_start(orm.TransientModel):
    _name = 'picking.dispatch.start'
    _description = 'Picking Dispatch Start'

    def start(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        dispatch_ids = context.get('active_ids')
        if not dispatch_ids:
            raise orm.except_orm(
                _('Error'),
                _('No selected picking dispatch'))

        dispatch_obj = self.pool['picking.dispatch']
        domain = [('state', '=', 'assigned'),
                  ('id', 'in', dispatch_ids)]
        check_ids = dispatch_obj.search(cr, uid, domain, context=context)
        if dispatch_ids != check_ids:
            raise orm.except_orm(
                _('Error'),
                _('All the picking dispatches must be assigned to '
                  'be started.'))

        dispatch_obj.action_progress(cr, uid, dispatch_ids, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Started Picking Dispatch'),
            'res_model': 'picking.dispatch',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'target': 'current',
            'domain': [('id', 'in', dispatch_ids)],
            'nodestroy': True,
        }
