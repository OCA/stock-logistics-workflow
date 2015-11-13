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
from openerp import models, api, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def unlink(self):
        for invoice in self:
            invoice.invoice_line.update_stock_moves()
        return super(AccountInvoice, self).unlink()


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    stock_moves = fields.Many2many('stock.move',
                                   'stock_move_invoice_rel',
                                   'invoice_line_id', 'move_id',
                                   'Stock Moves', readonly=True)

    @api.multi
    def update_stock_moves(self):
        if 'stock_invoice_onshipping' in self.env.context:
            return False
        for line in self:
            move_obj = self.env['stock.move']
            moves = move_obj.search([('invoice_lines', '=', line.id)])
            if moves:
                move = moves[0]
                move.write({'invoice_state': '2binvoiced'})
        return True

    @api.multi
    def unlink(self):
        self.update_stock_moves()
        return super(AccountInvoiceLine, self).unlink()
