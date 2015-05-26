# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, api, fields, exceptions, _



class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def unlink(self):
        cr = self.env.cr
        for invoice in self:
            for line in invoice.invoice_line:
                move_obj = self.env['stock.move']
                cr.execute("""
                SELECT move_id
                FROM stock_move_invoice_rel
                WHERE invoice_line_id = %s
                """, (line.id, ))
                res = cr.fetchone()
                if res:
                    move_id = res[0]
                    move = move_obj.browse(move_id)
                    move.write({'invoice_state': '2binvoiced'})
        return super(AccountInvoice, self).unlink()


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.multi
    def unlink(self):
        cr = self.env.cr
        for line in self:
            if 'stock_invoice_onshipping' in self.env.context:
                continue
            move_obj = self.env['stock.move']
            cr.execute("""
            SELECT move_id
            FROM stock_move_invoice_rel
            WHERE invoice_line_id = %s
            """, (line.id, ))
            res = cr.fetchone()
            if res:
                move_id = res[0]
                move = move_obj.browse(move_id)
                move.write({'invoice_state': '2binvoiced'})
        return super(AccountInvoiceLine, self).unlink()

    @api.multi
    def write(self, vals):
        cr = self.env.cr
        res = super(AccountInvoiceLine, self).write(vals)
        if 'quantity' in vals:
            for line in self:
                move_obj = self.env['stock.move']
                cr.execute("""
                SELECT move_id
                FROM stock_move_invoice_rel
                WHERE invoice_line_id = %s
                """, (line.id, ))
                res = cr.fetchone()
                if res:
                    move_id = res[0]
                    move = move_obj.browse(move_id)
                    product_qty = move.product_uos_qty or move.product_qty
                    if move.invoiced_qty > product_qty:
                        raise exceptions.Warning(
                            _('Error!'),
                            _("""You are trying to invoice more quantity
                            than what has actually been received or
                            delivered."""))
                    if move.invoiced_qty != product_qty:
                        invoice_state = '2binvoiced'
                    else:
                        invoice_state = 'invoiced'
                    move.write({'invoice_state': invoice_state})
        return res