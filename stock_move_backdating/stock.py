# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp.osv import fields, orm
from datetime import datetime
from dateutil import tz
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_move(orm.Model):
    _name = "stock.move"
    _inherit = _name

    def check_date_backdating(self, cr, uid, ids, context=None):
        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for stock_move in self.browse(
                cr, uid, ids, context=context):
            if stock_move.date_backdating and \
                    stock_move.date_backdating > now:
                return False
        return True

    _columns = {
        'date_backdating': fields.datetime(
            "Actual Movement Date", readonly=False,
            states={
                'done': [('readonly', True)], 'cancel': [('readonly', True)]},
            help="Date when the move action was committed. "
            "Will set the move date to this date instead "
                 "of current date when processing to done."
        ),
    }

    _constraints = [
        (check_date_backdating,
         _('You can not process an actual movement date in the future.'),
         ['date_backdating']),
    ]

    def action_done(self, cr, uid, ids, context=None):
        # look at previous state and find date_backdating
        backdating_dates = {}

        for move in self.browse(cr, uid, ids, context=context):
            # if not already in done and date is given
            if (move.state != 'done') and (move.date_backdating):
                backdating_dates[move.id] = move.date_backdating

        # do actual processing
        result = super(stock_move, self).action_done(cr, uid, ids, context)

        # overwrite date field where applicable
        for move in self.browse(cr, uid, backdating_dates.keys(),
                                context=context):
            self.write(
                cr,
                uid,
                [move.id],
                {'date': backdating_dates[move.id]},
                context=context
            )

        return result

    def on_change_date_backdating(self, cr, uid, ids, date_backdating,
                                  context=None):
        """ Test if date is in the past
        @param date_backdating: date
        """
        # do nothing if empty
        if (not date_backdating):
            return {}

        dt = datetime.strptime(date_backdating, DEFAULT_SERVER_DATETIME_FORMAT)
        now = datetime.now()

        if (dt > now):
            warning = {'title': _('Error!'), 'message': _(
                'You can not process an actual movement date in the future.')}
            # Delete values (old code) because it shows many times
            # the warning message
            # It looks like a bug in Odoo.
            return {'warning': warning}

        # otherwise, ok
        return {}

    def _create_account_move_line(self, cr, uid, move, src_account_id,
                                  dest_account_id, reference_amount,
                                  reference_currency_id, context=None):
        def _convert_date(from_date):
            from_zone = tz.tzutc()
            to_zone = tz.gettz(context.get('tz'))
            utc = datetime.strptime(from_date, DEFAULT_SERVER_DATETIME_FORMAT)
            utc = utc.replace(tzinfo=from_zone)
            to_date = utc.astimezone(to_zone)
            to_date = to_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            return to_date[:10]

        if context is None:
            context = {}
        res = super(stock_move, self)._create_account_move_line(
            cr, uid, move,
            src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=context
        )
        for o2m_tuple in res:
            date = False
            if move.date_backdating:
                date = _convert_date(move.date_backdating)
            elif move.date:
                date = _convert_date(move.date)
            o2m_tuple[2]['date'] = date
            if 'move_date' not in context:
                context['move_date'] = date
        return res
