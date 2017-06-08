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


class StockMove(models.Model):

    @api.one
    def calc_invoiced_qty(self):
        invoiced_qty = 0.0
        for invoice_line in self.invoice_lines:
            invoiced_qty += invoice_line.quantity
        self.invoiced_qty = invoiced_qty

    _inherit = 'stock.move'

    invoiced_qty = fields.Float('Invoiced quantity',
                                compute="calc_invoiced_qty",)
    invoice_lines = fields.Many2many('account.invoice.line',
                                     'stock_move_invoice_rel',
                                     'move_id', 'invoice_line_id',
                                     'Invoice Lines', readonly=True)

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        invl = super(StockMove, self)._create_invoice_line_from_vals(
            move, invoice_line_vals)
        move.write({'invoice_lines': [(4, invl)]})
        return invl
