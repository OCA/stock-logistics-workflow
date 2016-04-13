# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class CheckAssignAll(models.TransientModel):
    _name = 'picking.dispatch.check.assign.all'
    _description = 'Picking Dispatch Check Availability'

    @api.multi
    def check(self):

        dispatch_ids = self.env.context.get('active_ids')
        if not dispatch_ids:
            raise except_orm(_('Error'), _('No selected dispatch'))

        dispatchs = self.env['picking.dispatch'].browse(dispatch_ids)
        dispatchs.check_assign_all()
        return {'type': 'ir.actions.act_window_close'}
