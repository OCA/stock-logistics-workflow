# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class StockUnassignWizard(models.TransientModel):
    _name = 'stock.unassign.wizard'

    line_ids = fields.One2many(
        comodel_name='stock.unassign.wizard.line', inverse_name='wizard_id',
        string='Lines')


class StockUnassignWizardLine(models.TransientModel):
    _name = 'stock.unassign.wizard.line'

    wizard_id = fields.Many2one(
        comodel_name='stock.unassign.wizard', string='Wizard')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    picking_id = fields.Many2one(
        comodel_name='stock.picking', string='Picking')
    move_id = fields.Many2one(
        comodel_name='stock.move', string='Picking')

    @api.multi
    def unassign_line(self):
        self.ensure_one()

        # Unassign stock:
        self.move_id.do_unreserve()
        # Remove current line from wizard:
        wizard_id = self.wizard_id.id
        self.write({
            'wizard_id': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Unassign Wizard'),
            'res_model': 'stock.unassign.wizard',
            'res_id': wizard_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
