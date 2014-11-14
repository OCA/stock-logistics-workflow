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

from openerp.osv import orm, fields


class StockPicking(orm.Model):

    _inherit = 'stock.picking'

    def _move_trigger(self, cr, uid, ids, context=None):
        move_obj = self.pool['stock.move']
        picking_ids = set()
        for move in move_obj.browse(cr, uid, ids, context=context):
            picking_ids.add(move.picking_id.id)

        return list(picking_ids)

    def _set_date_expected(self, cr, uid, ids, name, value, arg, context=None):
        """Update all lines to have the same date.

        This is different from the existing min_date field. We leave min_date
        alone because it is used when moving pickings in the calendar view.
        """

        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]

        move_ids = []

        for picking in self.browse(cr, uid, ids, context=context):
            move_ids += [move.id for move in picking.move_lines]

        self.pool['stock.move'].write(cr, uid, move_ids, {
            name: value
        }, context=context)

        return True

    def _get_date_expected(self, cr, uid, ids, field_names, arg, context=None):
        """When read, this field behaves like the existing min_date field"""

        result = super(StockPicking, self).get_min_max_date(
            cr, uid, ids, field_names, arg, context)

        for key in result:
            result[key].update({
                'date_expected': result[key]['min_date']
            })

        return result

    _columns = {
        'date_expected': fields.function(
            _get_date_expected,
            fnct_inv=_set_date_expected,
            type='datetime',
            string='Scheduled Time',
            multi="min_max_date",
            help="Scheduled time for the shipment to be processed. Changing "
            "this field will update all the lines in the picking.",
            store={
                'stock.move': (
                    _move_trigger, ['date_expected'], 40
                )
            }),
    }


class StockPickingIn(orm.Model):

    """Manually bring here what is done above in the stock.picking.

    This is common workaround. For example, it is done that way in the core
    delivery module.

    """
    _inherit = 'stock.picking.in'

    def _move_trigger(self, *args, **kwargs):
        return self.pool['stock.picking']._move_trigger(*args, **kwargs)

    def _set_date_expected(self, *args, **kwargs):
        return self.pool['stock.picking']._set_date_expected(*args, **kwargs)

    def _get_date_expected(self, *args, **kwargs):
        return self.pool['stock.picking']._get_date_expected(*args, **kwargs)

    _columns = {
        'date_expected': fields.function(
            _get_date_expected,
            fnct_inv=_set_date_expected,
            type='datetime',
            string='Scheduled Time',
            multi="min_max_date",
            help="Scheduled time for the shipment to be processed",
            store={
                'stock.move': (
                    _move_trigger, ['date_expected'], 40
                )
            }),
    }


class StockPickingOut(orm.Model):

    """Manually bring here what is done above in the stock.picking."""

    _inherit = 'stock.picking.out'

    def _move_trigger(self, *args, **kwargs):
        return self.pool['stock.picking']._move_trigger(*args, **kwargs)

    def _set_date_expected(self, *args, **kwargs):
        return self.pool['stock.picking']._set_date_expected(*args, **kwargs)

    def _get_date_expected(self, *args, **kwargs):
        return self.pool['stock.picking']._get_date_expected(*args, **kwargs)

    _columns = {
        'date_expected': fields.function(
            _get_date_expected,
            fnct_inv=_set_date_expected,
            type='datetime',
            string='Scheduled Time',
            multi="min_max_date",
            help="Scheduled time for the shipment to be processed",
            store={
                'stock.move': (
                    _move_trigger, ['date_expected'], 40
                )
            }),
    }
