# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# © 2014 GRAP (Sylvain Le Gal)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, api, fields, models
from openerp.exceptions import UserError


class CheckAssignAll(models.TransientModel):
    _name = 'stock.picking.check.assign.all'
    _description = 'Delivery Orders Check Availability'

    @api.multi
    def _default_force_availability(self):
        return self.env.context.get('force_availability', False)

    @api.multi
    def _default_process_picking(self):
        return self.env.context.get('process_picking', False)

    check_availability = fields.Boolean(
        'Check Availability',
        default=True,
        help="""check this box if you want to check the availability of """
        """the selected Delivery Orders.""")
    force_availability = fields.Boolean(
        'Force Availability',
        default='_default_force_availability',
        help="""check this box if you want to force the availability of """
        """the selected Delivery Orders.""")
    process_picking = fields.Boolean(
        'Deliver',
        default='_default_process_picking',
        help="""check this box if you want to deliver all the selected """
        """Delivery Orders.\n You'll not have the possibility to realize a """
        """partial delivery.\n If you want to do that, please do it """
        """manually on the Delivery Order form.""")

    @api.multi
    def check(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        immediate_transfer_obj = self.env['stock.immediate.transfer']
        picking_ids = self.env.context.get('active_ids')

        if not picking_ids:
            raise UserError(_('No selected delivery orders'))

        # Get confirmed pickings
        domain = [('picking_type_code', '=', 'outgoing'),
                  ('state', '=', 'confirmed'),
                  ('id', 'in', picking_ids)]
        confirmed_pickings = picking_obj.search(domain, order='min_date')

        # Assign all picking if asked
        if self.check_availability and confirmed_pickings:
            confirmed_pickings.check_assign_all()

        # Force availability if asked
        if self.force_availability and confirmed_pickings:
            confirmed_pickings.force_assign()

        # Get all pickings ready to deliver
        domain = [('picking_type_code', '=', 'outgoing'),
                  ('state', '=', 'assigned'),
                  ('id', 'in', picking_ids)]
        assigned_pickings = picking_obj.search(domain, order='min_date')

        # Process all pickings if asked
        if self.process_picking and assigned_pickings:
            for picking in assigned_pickings:
                wizard = immediate_transfer_obj.create(
                    {'pick_id': picking.id})
                wizard.process()

        return True
