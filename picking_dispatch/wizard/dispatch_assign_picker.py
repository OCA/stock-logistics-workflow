# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models

from openerp.exceptions import UserError


class DispatchAssignPicker(models.TransientModel):
    _name = 'picking.dispatch.assign.picker'
    _description = 'Picking Dispatch Assign Picker'

    picker_id = fields.Many2one(
        'res.users',
        string='Picker',
        required=True
    )

    @api.multi
    def assign_picker(self):
        self.ensure_one()

        dispatch_ids = self.env.context.get('active_ids')
        if not dispatch_ids:
            raise UserError(_('No selected picking dispatch'))

        # filter out dispatches with a state on which we must not
        # change the picker
        dispatches = self.env['picking.dispatch'].search([
            ('state', '=', 'draft'),
            ('id', 'in', dispatch_ids)
        ])

        if not dispatches:
            raise UserError(_("Cannot assign dispatch(es) "
                              "with a state not equal to 'draft'"))
        else:
            dispatches.write({'picker_id': self.picker_id.id})
            dispatches.action_assign()
