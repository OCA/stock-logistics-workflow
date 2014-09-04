# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
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
import datetime as dt

from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT

_logger = logging.getLogger(__name__)


class PlanFinished(Exception):
    """The available future stock is insufficient to handle all deliveries.

    After that is raised, we could stop processing the remaining deliveries,
    or consider that a failure of the whole process.

    Especially in the first case, you could argue this is an exception for
    control flow, and should then be factored out.

    """
    pass


class StockPickingOut(orm.Model):

    _inherit = 'stock.picking.out'

    def _availability_plan(self, cr, uid, product, context=None):
        user_obj = self.pool['res.users']
        move_obj = self.pool['stock.move']

        stock_now = product.qty_available
        security_days = user_obj.browse(
            cr, uid, uid, context=context
        ).company_id.security_lead
        security_delta = dt.timedelta(days=security_days)
        today = dt.datetime.today()

        plan = [{'date': today + security_delta, 'quantity': stock_now}]

        move_in_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product.id),
            ('picking_id.type', '=', 'in'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date_expected', context=context)

        for move_in in move_obj.browse(cr, uid, move_in_ids, context=context):
            plan.append({
                'date': dt.datetime.strptime(move_in.date_expected, DT_FORMAT)
                + security_delta,
                'quantity': move_in.product_qty
            })
        return iter(plan)

    def compute_delivery_dates(self, cr, uid, product, context=None):
        if product.procure_method == 'make_to_stock':
            return self.compute_mts_delivery_dates(cr, uid, product, context)
        else:
            raise orm.except_orm(
                u'Not implemented',
                u'Computing delivery dates for Make To Order products is not '
                u'implemented yet.')

    def compute_mts_delivery_dates(self, cr, uid, product, context=None):
        move_obj = self.pool['stock.move']

        plan = self._availability_plan(cr, uid, product, context=context)

        move_out_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product.id),
            ('picking_id.type', '=', 'out'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date_expected', context=context)

        current_plan = plan.next()

        try:
            for move_out in move_obj.browse(cr, uid, move_out_ids,
                                            context=context):
                remaining_out_qty = move_out.product_qty

                while remaining_out_qty > 0.0:
                    if current_plan['quantity'] >= remaining_out_qty:
                        current_plan['quantity'] -= remaining_out_qty
                        new_date_str = dt.datetime.strftime(
                            current_plan['date'], DT_FORMAT
                        )
                        move_obj.write(cr, uid, move_out.id, {
                            'date_expected': new_date_str,
                        }, context=context)
                        remaining_out_qty = 0.0
                    else:
                        remaining_out_qty -= current_plan['quantity']
                        try:
                            current_plan = plan.next()
                        except StopIteration:
                            raise PlanFinished
        except PlanFinished:
            _logger.info(
                u'There is not enough planned stock to set dates for all '
                u'outgoing moves. Remaining ones are left untouched.'
            )
        return True

    def compute_all_delivery_dates(self, cr, uid, context=None):
        move_obj = self.pool['stock.move']
        prod_obj = self.pool['product.product']

        moves_out_grouped = move_obj.read_group(
            cr,
            uid,
            domain=[
                ('picking_id.type', '=', 'out'),
                ('state', 'in', ('confirmed', 'assigned', 'pending'))
            ],
            fields=['product_id'],
            groupby=['product_id'],
            context=context,
        )

        product_ids = [g['product_id'][0] for g in moves_out_grouped]

        for product in prod_obj.browse(cr, uid, product_ids, context=context):
            self.compute_delivery_dates(cr, uid, product, context=context)

        return True
