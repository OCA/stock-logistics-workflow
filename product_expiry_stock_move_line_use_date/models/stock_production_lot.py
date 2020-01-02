# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        if self.env.context.get('copy_date_name_to_lot'):
            move_line = self.env['stock.move.line'].search(
                [
                    ('id', 'in', self.env.context.get('copy_date_name_to_lot_mls')),
                    ('lot_name', '=', vals.get('name'))
                ]
            )
            if move_line:
                vals.update({
                    'use_date': move_line.lot_use_date_name,
                })
        return super().create(vals)
