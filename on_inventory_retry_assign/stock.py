# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2014 Camptocamp SA
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
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class stock_inventory(orm.Model):

    _inherit = "stock.inventory"

    def action_done(self, cr, uid, ids, context=None):
        res = super(stock_inventory, self).action_done(
            cr, uid, ids, context=context)
        self._retry_assign_pickings(cr, uid, ids, context=context)
        return res

    def _retry_assign_pickings(self, cr, uid, ids, context=None):
        """ Retry to assign pickings impacted by the inventory.

        If a quantity of products has been reduced, pickings could
        not be available anymore.

        Search all the pickings having moves on the products for which
        quantity has been modified in the inventory. For these pickings,
        cancel their availability and check again their availability.

        """
        move_obj = self.pool['stock.move']
        picking_obj = self.pool['stock.picking']

        product_ids = set()
        for inventory in self.browse(cr, uid, ids, context=context):
            for move in inventory.move_ids:
                product_ids.add(move.product_id.id)

        move_ids = move_obj.search(
            cr, uid,
            [('product_id', 'in', list(product_ids)),
             ('picking_id.state', '=', 'assigned'),
             ('picking_id.type', '!=', 'in')],
            context=context)
        picking_ids = set()
        for move in move_obj.browse(cr, uid, move_ids, context=context):
            picking_ids.add(move.picking_id.id)
        # apply the 'order by' on the ids so they will be assigned
        # in the correct order
        picking_ids = picking_obj.search(cr, uid,
                                         [('id', 'in', list(picking_ids))],
                                         order='min_date',
                                         context=context)
        picking_obj.retry_assign(cr, uid, picking_ids, context=context)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def retry_assign(self, cr, uid, ids, context=None):
        """ Cancel availability of pickings and check it again """
        self.cancel_assign(cr, uid, ids, context)
        _logger.info('try reassign pickings %s', ids)
        errors = []
        for picking_id in ids:
            try:
                self.action_assign(cr, uid, [picking_id], context)
            except orm.except_orm, exc:
                name = self.read(cr, uid, picking_id, ['name'],
                                 context=context)['name']
                errors.append(u'%s: %s' % (name, exc.args[-1]))
                _logger.info('error in action_assign for picking %s: %s',
                             name, exc)
        if errors:
            message = '\n'.join(errors)
            raise orm.except_orm(_(u'Warning'),
                                 _(u'No operations validated due '
                                   'to the following errors:\n%s') % message)
        return True
