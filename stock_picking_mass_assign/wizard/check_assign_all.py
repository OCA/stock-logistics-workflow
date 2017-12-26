# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# © 2014 GRAP (Sylvain Le Gal)
# © 2017 JARSA Sistemas S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class CheckAssignAll(models.TransientModel):
    _name = 'stock.picking.check.assign.all'
    _description = 'Delivery Orders Check Availability'

    @api.multi
    def _default_process_picking(self):
        return self.env.context.get('process_picking', False)

    check_availability = fields.Boolean(
        'Check Availability',
        default=True,
        help="""check this box if you want to check the availability of """
        """the selected Delivery Orders.""")
    process_picking = fields.Boolean(
        'Transfer',
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
        picking_ids = self._context.get('active_ids')

        if not picking_ids:
            raise ValidationError(_('No selected delivery orders'))

        # Get confirmed pickings
        domain = [('state', '=', 'confirmed'), ('id', 'in', picking_ids)]
        confirmed_pickings = picking_obj.search(domain)

        # Assign all picking if asked
        if self.check_availability and confirmed_pickings:
            confirmed_pickings.check_assign_all()

        # Get all pickings ready to deliver
        domain = [('state', '=', 'assigned'), ('id', 'in', picking_ids)]
        assigned_pickings = picking_obj.search(domain)

        # Process all pickings if asked
        if self.process_picking and assigned_pickings:
            wizard = immediate_transfer_obj.create({
                'pick_ids': [(6, 0, assigned_pickings.ids)],
            })
            wizard.process()
        return True
