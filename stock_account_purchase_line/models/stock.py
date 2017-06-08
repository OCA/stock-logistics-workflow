# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, orm


class StockMove(orm.Model):

    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type,
                               context=None):
        res = super(StockMove, self)._get_invoice_line_vals(cr, uid,
                                                            move, partner,
                                                            inv_type,
                                                            context=context)
        if move.purchase_line_id:
            res['purchase_line_od'] = move.purchase_line_id.id
        return res


class StockQuant(orm.Model):
    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost,
                                   credit_account_id, debit_account_id,
                                   context=None):
        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context)
        for line in res:
            line[2]['purchase_line_id'] = move.purchase_line_id.id
        return res
