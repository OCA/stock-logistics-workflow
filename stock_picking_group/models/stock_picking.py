# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_group_id = fields.Many2one(
        comodel_name='stock.picking.group', string='Group')

    @api.multi
    def group_pickings(self):
        picking_group_obj = self.env['stock.picking.group']

        picking_ids = self.ids
        if len(picking_ids) < 2:
            raise UserError(_('You must select more than one picking.'))

        new_group = picking_group_obj.create({
            'picking_ids': [(6, 0, picking_ids)],
        })

        return {
            'name': _('Sales Order(s)'),
            'res_id': new_group.id,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking.group',
            'target': 'current',
        }
