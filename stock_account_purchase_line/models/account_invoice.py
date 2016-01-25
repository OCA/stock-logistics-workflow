# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, orm


class AccountInvoiceLine(orm.Model):

    _inherit = 'account.invoice.line'

    _columns = {
        'purchase_line_id': fields.many2one('purchase.order.line',
                                            'Purchase Order Line',
                                            ondelete='set null', select=True),
    }

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(AccountInvoiceLine, self).move_line_get_item(
                cr, uid, line, context=context)
        if line.purchase_line_id and res:
            res['purchase_line_id'] = line.purchase_line_id.id
        return res


class AccountInvoice(orm.Model):

    _inherit = 'account.invoice'

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(AccountInvoice, self).line_get_convert(
                cr, uid, x, part, date, context=context)
        if x.get('purchase_line_id', False):
            res['purchase_line_id'] = x.get('purchase_line_id')
        return res
