# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def open_unassign_wizard(self):
        self.ensure_one()
        unassign_wizard_obj = self.env['stock.unassign.wizard']

        confirmed_moves = self.search([
            ('product_id', '=', self.product_id.id),
            ('state', 'in', ['assigned', 'partially_available']),
            '|',
            '&',
            '&',
            ('picking_id', '!=', False),
            ('picking_id', '!=', self.picking_id.id),
            ('picking_type_id.code', 'in', ('outgoing', 'internal')),
            '&',
            ('raw_material_production_id', '!=', False),
            ('raw_material_production_id', '!=', self.raw_material_production_id.id),
        ])

        wizard_lines_vals = []
        for move in confirmed_moves:
            cur_vals = {
                'product_id': move.product_id.id,
                'picking_id': move.picking_id.id,
                'move_id': move.id,
                'raw_material_production_id':
                    move.raw_material_production_id.id,
                'partner_id': move.partner_id.id,
            }
            wizard_lines_vals.append((0, False, cur_vals))
        wizard = unassign_wizard_obj.create({
            'line_ids': wizard_lines_vals,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Unassign Wizard'),
            'res_model': 'stock.unassign.wizard',
            'res_id': wizard.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
