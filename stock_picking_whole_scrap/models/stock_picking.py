# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_whole_scrap(self):
        self.ensure_one()
        return {
            'name': _('Whole Scrap'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.stock.picking.scrap',
            'type': 'ir.actions.act_window',
            'context': {'default_picking_id': self.id},
            'target': 'new',
        }
