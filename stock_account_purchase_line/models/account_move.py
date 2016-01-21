# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class AccountMoveLine(orm.Model):

    _inherit = 'account.move.line'

    _columns = {
        'purchase_line_id': fields.many2one('purchase.order.line',
                                            'Purchase Order Line',
                                            ondelete='set null', select=True),
    }
