# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, api
from odoo.models import TransientModel


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

    @api.multi
    def mass_action(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
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
            domain = [('state', 'not in', ['draft', 'cancel', 'done']),
                      ('id', 'in', picking_ids)]
            pickings_to_check = picking_obj.search(domain, order='min_date')
            pickings_to_check.action_assign()

        # Force availability if asked
        if self.force_availability:
            confirmed_picking_lst.force_assign()

        # Get all pickings ready to transfer and transfer them if asked
        if self.transfer:
            domain = [('state', '=', 'assigned'),
                      ('id', 'in', picking_ids)]
            assigned_picking_lst = picking_obj.search(domain, order='min_date')
            for picking in assigned_picking_lst:
                picking.do_transfer()
