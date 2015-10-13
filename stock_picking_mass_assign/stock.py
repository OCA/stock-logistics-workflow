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
import logging

from openerp.osv import orm

_logger = logging.getLogger(__name__)


class stock_picking(orm.Model):

    _inherit = 'stock.picking'

    def check_assign_all(self, cr, uid, ids=None, context=None):
        """ Try to assign confirmed pickings """
        if isinstance(ids, (int, long)):
            ids = [ids]
        if ids is None:
            domain = [('type', '=', 'out'),
                      ('state', '=', 'confirmed')]
            ids = self.search(cr, uid, domain,
                              order='min_date',
                              context=context)

        for picking_id in ids:
            try:
                self.action_assign(cr, uid, [picking_id], context)
            except orm.except_orm:
                # ignore the error, the picking will just stay as confirmed
                name = self.read(cr, uid, picking_id, ['name'],
                                 context=context)['name']
                _logger.info('error in action_assign for picking %s',
                             name, exc_info=True)
        return True
