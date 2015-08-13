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

from openerp import models, api


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        # do actual processing
        result = super(stock_move, self).action_done()
        # overwrite date field where applicable
        for move in self:
            if move.linked_move_operation_ids:
                operation = move.linked_move_operation_ids[0]
                move.write(
                    {
                        'date': operation.operation_id.date
                    }
                )
                move.refresh()
                if move.quant_ids:
                    for quant in move.quant_ids:
                        quant.write({'in_date': move.date})

        return result


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
            if move.date:
                date = move.date[:10]
            o2m_tuple[2]['date'] = date
            if 'move_date' not in self._context:
                res = res.with_context(move_date=date)
        return res
