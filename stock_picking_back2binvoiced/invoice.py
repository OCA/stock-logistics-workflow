# -*- coding: utf-8 -*-
#############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author Florian da Costa <florian.dacosta@akretion.com>
#
#############################################################################

from openerp.osv import orm


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    def unlink(self, cr, uid, ids, context=None):
        picking_ids = []
        invoices = self.read(cr, uid, ids, ['picking_ids'], context=context)
        for inv in invoices:
            if inv['picking_ids']:
                picking_ids += inv['picking_ids']
        res = super(AccountInvoice, self).unlink(
            cr, uid, ids, context=context)
        self.pool['stock.picking'].write(
            cr, uid, picking_ids, {'invoice_state': '2binvoiced'})
        return res
