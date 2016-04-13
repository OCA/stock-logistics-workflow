# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class dispatch_assign_picker(orm.TransientModel):
    _name = 'picking.dispatch.assign.picker'
    _description = 'Picking Dispatch Assign Picker'

    _columns = {
        'picker_id': fields.many2one(
            'res.users',
            string='Picker',
            required=True),
    }

    def assign_picker(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        dispatch_ids = context.get('active_ids')
        if not dispatch_ids:
            raise orm.except_orm(
                _('Error'),
                _('No selected picking dispatch'))

        assert len(ids) == 1, "1 ID expected, got: %s" % (ids, )
        form = self.browse(cr, uid, ids[0], context=context)

        dispatch_obj = self.pool['picking.dispatch']
        # filter out dispatches with a state on which we must not
        # change the picker
        domain = [('state', '=', 'draft'),
                  ('id', 'in', dispatch_ids)]
        dispatch_ids = dispatch_obj.search(cr, uid, domain, context=context)
        dispatch_obj.write(cr, uid, dispatch_ids,
                           {'picker_id': form.picker_id.id},
                           context=context)
        dispatch_obj.action_assign(cr, uid, dispatch_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
