# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AssignManualQuants(models.TransientModel):
    _inherit = 'assign.manual.quants'

    @api.multi
    def assign_quants(self):
        super(AssignManualQuants, self).assign_quants()
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        move.picking_id._delete_packages_information()
        return {}
