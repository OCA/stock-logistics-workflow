# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, osv


class stock_move(osv.Model):
    _inherit = "stock.move"

    _columns = {
        'account_analytic_id': fields.many2one('account.analytic.account',
                                               'Analytic account'),
    }

    def _create_account_move_line(self, cr, uid, move, src_account_id,
                                  dest_account_id, reference_amount,
                                  reference_currency_id, context=None):
        res = super(stock_move,
                    self)._create_account_move_line(cr, uid,
                                                    move,
                                                    src_account_id,
                                                    dest_account_id,
                                                    reference_amount,
                                                    reference_currency_id,
                                                    context=context
                                                    )
        if move.account_analytic_id:
            for _val1, _val2, vals in res:
                vals['analytic_account_id'] = move.account_analytic_id.id
        return res


class stock_quant(osv.Model):

    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost,
                                   credit_account_id, debit_account_id,
                                   context=None):
        res = super(stock_quant,
                    self)._prepare_account_move_line(cr,
                                                     uid, move, qty, cost,
                                                     credit_account_id,
                                                     debit_account_id,
                                                     context=context
                                                     )
        # Add analytic account in debit line
        res[0][2].update({
                            'analytic_account_id': move.account_analytic_id.id,
                                })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
