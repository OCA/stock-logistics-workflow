#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
#    Contributor: Pedro M. Baeza
#    Copyright 2015 Serv. Tecnol. Avanzados
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
from openerp.tools.translate import _


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    @api.model
    def _get_journal_type(self):
        res_ids = self.env.context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(res_ids)
        pick = pickings and pickings[0]
        if pick.move_lines:
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage
            if src_usage == 'supplier' and dest_usage == 'customer':
                moves = pick.move_lines.filtered('purchase_line_id')
                moves = moves and moves[0]
                pick_purchase = (
                    moves.purchase_line_id.order_id.invoice_method ==
                    'picking')
                return "purchase" if pick_purchase else "sale"
        return super(StockInvoiceOnshipping, self)._get_journal_type()

    def _default_second_journal(self):
        res = self.env['account.journal'].search([('type', '=', 'sale')])
        return res and res[0] or False

    def _need_two_invoices(self):
        if 'active_id' in self.env.context:
            pick = self.env['stock.picking'].browse(
                self.env.context['active_id'])
            so = pick.sale_id
            moves = pick.move_lines.filtered('purchase_line_id')
            moves = moves and moves[0]
            return (so.order_policy == 'picking' and
                    moves.purchase_line_id.order_id.invoice_method ==
                    'picking')
        return False

    @api.depends('journal_type', 'need_two_invoices')
    def _get_wizard_title(self):
        if self.need_two_invoices:
            self.wizard_title = _("Create Two Invoices")
        else:
            selection = dict(self.fields_get()['journal_type']['selection'])
            journal_type = self._get_journal_type()
            self.wizard_title = selection[journal_type]

    @api.multi
    def open_invoice(self):
        res = super(StockInvoiceOnshipping, self).open_invoice()
        if self.need_two_invoices:
            res['view_id'] = self.env.ref('account.invoice_tree').id
            res['name'] = _('Invoices')
            res['view_mode'] = 'tree'
            del res['views']
            del res['display_name']
        return res

    @api.multi
    def create_invoice(self):
        if self.need_two_invoices:
            picking_ids = self.env.context['active_ids']
            picking_model = self.env['stock.picking']
            pickings = picking_model.browse(picking_ids)
            # Group picking by customer
            pickings_by_partner = {}
            for picking in pickings:
                if not pickings_by_partner.get(picking.partner_id):
                    pickings_by_partner[picking.partner_id] = picking_model
                pickings_by_partner[picking.partner_id] += picking
            first_invoice_ids = []
            for partner, pickings_grouped in pickings_by_partner.iteritems():
                first_invoice_ids += pickings_grouped.with_context(
                    partner_to_invoice_id=partner.id,
                    date_inv=self.invoice_date,
                    inv_type='in_invoice',
                ).action_invoice_create(
                    journal_id=self.journal_id.id,
                    group=self.group,
                    type='in_invoice',
                )
            # Allow to invoice again
            pickings.mapped('move_lines').filtered(
                lambda x: x.invoice_state == 'invoiced').write(
                {'invoice_state': '2binvoiced'})
            second_invoice_ids = pickings.with_context(
                date_inv=self.invoice_date,
                inv_type='out_invoice',
            ).action_invoice_create(
                journal_id=self.second_journal_id.id,
                group=self.group,
                type='out_invoice',
            )
            return first_invoice_ids + second_invoice_ids
        else:
            return super(StockInvoiceOnshipping, self).create_invoice()

    need_two_invoices = fields.Boolean('Need two invoices',
                                       default=_need_two_invoices)

    second_journal_id = fields.Many2one('account.journal',
                                        'Second Destination Journal',
                                        default=_default_second_journal)
    wizard_title = fields.Char('Wizard Title',
                               compute='_get_wizard_title',
                               readonly=True)
    journal_type = fields.Selection(default=_get_journal_type)
