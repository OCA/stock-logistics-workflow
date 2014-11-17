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
from openerp.tools.translate import _
from openerp import pooler

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

    def _security_delta(self, cr, uid, product, context=None):
        return dt.timedelta(days=product.company_id.security_lead or 0.0)

    def _availability_plan(self, cr, uid, product, context=None):
        move_obj = self.pool['stock.move']

        stock_now = product.qty_available
        today = dt.datetime.today()
        security_delta = self._security_delta(cr, uid, product, context)
        plan = [{'date': today + security_delta,
                 'quantity': stock_now,
                 'pick_in_name': _('initial stock')}]

        move_in_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product.id),
            ('picking_id.type', '=', 'in'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date_expected', context=context)

        for move_in in move_obj.browse(cr, uid, move_in_ids, context=context):
            plan.append({
                'date': dt.datetime.strptime(move_in.date_expected, DT_FORMAT)
                + security_delta,
                'quantity': move_in.product_qty,
                'pick_in_name': move_in.picking_id.name
            })
        return iter(plan)

    def compute_delivery_dates(self, cr, uid, product, context=None):
        if product.procure_method == 'make_to_stock':
            return self.compute_mts_delivery_dates(cr, uid, product, context)
        else:
            return self.compute_mto_delivery_dates(cr, uid, product, context)

    def compute_mto_delivery_dates(self, cr, uid, product, context=None):
        move_obj = self.pool['stock.move']
        security_delta = self._security_delta(cr, uid, product, context)

        move_out_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product.id),
            ('picking_id.type', '=', 'out'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], context=context)

        for move_out in self.pool['stock.move'].browse(cr, uid, move_out_ids,
                                                       context=context):
            move_in_ids = move_obj.search(cr, uid, [
                ('move_dest_id', '=', move_out.id)
            ], order="date_expected desc", context=context)
            if move_in_ids:
                move_in = move_obj.browse(cr, uid, move_in_ids[0],
                                          context=context)

                move_in_date = dt.datetime.strptime(
                    move_in.date_expected, DT_FORMAT
                )
                new_date_str = dt.datetime.strftime(
                    move_in_date + security_delta, DT_FORMAT
                )
                move_obj.write(cr, uid, move_out.id, {
                    'date_expected': new_date_str
                }, context=context)
                message = _("Scheduled date update to %s from %s") \
                    % (new_date_str, move_in.picking_id.name)
                # Post message on product
                self.pool['product.product'].message_post(
                    cr, uid, product.id, body=message, context=context
                )
                # Post message on stock picking
                self.message_post(cr, uid, move_out.picking_id.id,
                                  body=message, context=context)

    def compute_mts_delivery_dates(self, cr, uid, product, context=None):
        move_obj = self.pool['stock.move']

        plan = self._availability_plan(cr, uid, product, context=context)

        # outgoing moves are sorted by date (the creation date) and not by
        # expected date to avoid circular situation where a finished plan could
        # lead to moves changing order, and the result to not converge.
        move_out_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product.id),
            ('picking_id.type', '=', 'out'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date', context=context)

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
                        message = _("Scheduled date update to %s from %s") \
                            % (new_date_str, current_plan['pick_in_name'])
                        # Post message on product
                        self.pool['product.product'].message_post(
                            cr, uid, product.id, body=message, context=context
                        )
                        # Post message on stock picking
                        self.message_post(cr, uid, move_out.picking_id.id,
                                          body=message, context=context)
                        remaining_out_qty = 0.0
                    else:
                        remaining_out_qty -= current_plan['quantity']
                        try:
                            current_plan = plan.next()
                        except StopIteration:
                            raise PlanFinished
        except PlanFinished:
            _logger.debug(
                u'There is not enough planned stock to set dates for all '
                u'outgoing moves. Remaining ones are left untouched.'
            )
        return True

    def compute_all_delivery_dates(self, cr, uid, use_new_cursor=True,
                                   context=None):
        """Loop on all products that have moves, and process them one by one.

        This can take a few seconds per product, so the transaction can be
        very long-lived and easily interrupted. To avoid that, we create a new
        cursor that is committed for every product.

        The use_new_cursor can be used in cases where multiple transactions are
        harmful, like for automated testing.

        """
        move_obj = self.pool['stock.move']
        prod_obj = self.pool['product.product']

        if use_new_cursor:
            cr = pooler.get_db(cr.dbname).cursor()

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
        _logger.info('Computing delivery dates for %s products',
                     len(product_ids))

        for product in prod_obj.browse(cr, uid, product_ids, context=context):

            _logger.info('Computing delivery dates for product %s',
                         product.name)
            try:
                self.compute_delivery_dates(cr, uid, product,
                                            context=context)
                if use_new_cursor:
                    cr.commit()
            except:
                if use_new_cursor:
                    cr.rollback()
                _logger.exception(
                    'Could not update delivery date for product %s',
                    product.name)

        if use_new_cursor:
            cr.close()

        return True
