# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
