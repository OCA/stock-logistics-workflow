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


class check_assign_all(orm.TransientModel):
    _name = 'stock.picking.check.assign.all'
    _description = 'Delivery Orders Check Availability'

    def check(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        picking_ids = context.get('active_ids')
        if not picking_ids:
            raise orm.except_orm(
                _('Error'),
                _('No selected delivery orders'))

        picking_obj = self.pool['stock.picking']
        domain = [('type', '=', 'out'),
                  ('state', '=', 'confirmed'),
                  ('id', 'in', picking_ids)]
        picking_ids = picking_obj.search(cr, uid, domain,
                                         order='min_date',
                                         context=context)
        picking_obj.check_assign_all(cr, uid, picking_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
