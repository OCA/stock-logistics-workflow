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
