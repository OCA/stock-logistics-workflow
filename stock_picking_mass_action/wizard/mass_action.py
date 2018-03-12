# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

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
#
##############################################################################

from openerp import fields, api
from openerp.models import TransientModel
from openerp.tools.translate import _


class StockPickingMassAction(TransientModel):
    _name = 'stock.picking.mass.action'
    _description = 'Stock Picking Mass Action'

    @api.model
    def _default_check_availability(self):
        return self.env.context.get('check_availability', False)

    @api.model
    def _default_force_availability(self):
        return self.env.context.get('force_availability', False)

    @api.model
    def _default_transfer(self):
        return self.env.context.get('transfer', False)

    @api.model
    def _default_create_invoice(self):
        return self.env.context.get('create_invoice', False)

    confirm = fields.Boolean(
        string='Mark as Todo', default=True,
        help="check this box if you want to mark as Todo the"
        " selected Pickings.")

    check_availability = fields.Boolean(
        string='Check Availability', default=_default_check_availability,
        help="check this box if you want to check the availability of"
        " the selected Pickings.")

    force_availability = fields.Boolean(
        string='Force Availability', default=_default_force_availability,
        help="check this box if you want to force the availability"
        " of the selected Pickings.")

    transfer = fields.Boolean(
        string='Transfer', default=_default_transfer,
        help="check this box if you want to transfer all the selected"
        " pickings.\n You'll not have the possibility to realize a"
        " partial transfer.\n If you want  to do that, please do it"
        " manually on the picking form.""")

    create_invoice = fields.Boolean(
        'Create Invoices/Refunds', default=_default_create_invoice,
        help="check this box if you want to create Invoices or Refunds for"
        " all the selected Pickings.")

    @api.multi
    def mass_action(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        transfert_wizard_obj = self.env['stock.transfer_details']
        picking_ids = self.env.context.get('active_ids')

        # Get draft pickings and confirm them if asked
        if self.confirm:
            domain = [('state', '=', 'draft'),
                      ('id', 'in', picking_ids)]
            draft_picking_lst = picking_obj.search(domain, order='min_date')
            draft_picking_lst.action_confirm()

        # Get confirmed pickings
        domain = [('state', 'in', ['confirmed', 'partially_available']),
                  ('id', 'in', picking_ids)]
        confirmed_picking_lst = picking_obj.search(domain, order='min_date')

        # check availability if asked
        if self.check_availability:
            confirmed_picking_lst.check_assign_all()

        # Force availability if asked
        if self.force_availability:
            confirmed_picking_lst.force_assign()

        # Get all pickings ready to transfer and transfer them if asked
        if self.transfer:
            domain = [('state', '=', 'assigned'),
                      ('id', 'in', picking_ids)]
            assigned_picking_lst = picking_obj.search(domain, order='min_date')
            for picking in assigned_picking_lst:
                transfert_wizard = transfert_wizard_obj.with_context(
                    active_ids=picking.ids,
                    active_id=picking.id).create(
                        {'picking_id': picking.id})
                transfert_wizard.do_detailed_transfer()

        # Get all pickings ready to invoice and invoice them if asked
        if self.create_invoice:
            domain = [('invoice_state', '=', '2binvoiced'),
                      ('id', 'in', picking_ids)]
            to_invoice_pickings = picking_obj.search(domain, order='min_date')
            ctx = self.env.context.copy()
            ctx['active_ids'] = to_invoice_pickings.ids
            ctx['active_model'] = 'stock.picking'
            return {
                'name': _('Stock Invoice Onshipping'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.invoice.onshipping',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': ctx,
            }
