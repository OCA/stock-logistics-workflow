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

from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.one
    @api.constrains('date_backdating')
    def check_date_backdating(self):
        now = datetime.now().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        if self.date_backdating and \
                self.date_backdating > now:
            raise Warning(
                "You can not process an actual movement date in the future.")

    date_backdating = fields.Datetime(
        "Actual Movement Date", readonly=False,
        states={
            'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Date when the move action was committed. "
        "Will set the move date to this date instead "
        "of current date when processing to done."
    )

    # @api.multi
    # def action_done(self):
        # if not already in done and date is given
        # import pdb;pdb.set_trace()
        # self.filtered(
            # lambda m: (
                # (m.state != 'done') and (m.date_backdating)
            # )
        # )
        # look at previous state and find date_backdating
        # backdating_dates = {
            # m.id: m.date_backdating for m in self}

        # do actual processing
        # result = super(stock_move, self).action_done()

        # overwrite date field where applicable
        # for move in self:
            # self.write(
                # {'date': backdating_dates[move.id]},
            # )

        # return result

    @api.onchange('date_backdating')
    def on_change_date_backdating(self):
        """ Test if date is in the past
        @param date_backdating: date
        """
        # do nothing if empty
        if (not self.date_backdating):
            return {}

        dt = datetime.strptime(
            self.date_backdating, DEFAULT_SERVER_DATETIME_FORMAT)
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


class stock_quant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _create_account_move_line(
        self, quants, move, credit_account_id, debit_account_id, journal_id
    ):
        res = super(stock_quant, self)._create_account_move_line(
            quants, move, credit_account_id, debit_account_id, journal_id
        )
        for o2m_tuple in res:
            date = False
            if move.date_backdating:
                date = move.date_backdating[:10]
            elif move.date:
                date = move.date[:10]
            o2m_tuple[2]['date'] = date
            if 'move_date' not in self._context:
                res = res.with_context(move_date=date)
        return res
