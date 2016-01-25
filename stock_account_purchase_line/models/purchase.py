# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, orm


class PurchaseOrder(orm.Model):

    _inherit = 'purchase.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(PurchaseOrder, self)._prepare_inv_line(
                cr, uid, account_id, order_line, context=context)
        res['purchase_line_id'] = order_line.id
        return res
