#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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

from openerp import models, api, fields


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    @api.model
    def _get_journal_type(self):
        return super(StockInvoiceOnshipping, self)._get_journal_type()

    def _default_second_journal(self):
        return self.env['account.journal'].search([('type', '=', 'sale')])

    def _need_two_invoices(self):
        pick = self.env['stock.picking'].browse(self.env.context['active_id'])
        so = pick.sale_id
        po = pick.move_lines[0].purchase_line_id.order_id
        if so.order_policy == 'picking' and po.invoice_method == 'picking':
            return True
        else:
            return False

    need_two_invoices = fields.Boolean('Need two invoices',
                                       default=_need_two_invoices)

    second_journal_id = fields.Many2one('account.journal',
                                        'Second Destination Journal',
                                        default=_default_second_journal)
