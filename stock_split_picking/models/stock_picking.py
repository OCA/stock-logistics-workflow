# -*- coding: utf-8 -*-
# Copyright 2013-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        """Use to trigger the wizard from button with correct context"""
        self.ensure_one()
        wiz = self.env['stock.picking.split'].create({'picking_id': self.id})
        view = self.env.ref('stock_split_picking.stock_picking_split_form')
        return {
            'name': _('Split Picking'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking.split',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
