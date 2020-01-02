# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        # copy_date_name_to_lot_mls is set by stock.move.line._action_done
        # which is calling create in order to find the right move line whose
        # stock.production.lot is being created, as no clean extension hook
        # is available in Odoo
        move_line_ids = self.env.context.get('copy_date_name_to_lot_mls')
        if move_line_ids:
            move_line = self.env['stock.move.line'].search(
                [
                    ('id', 'in', move_line_ids),
                    ('product_id', '=', vals.get('product_id')),
                    ('lot_name', '=', vals.get('name'))
                ]
            )
            if move_line:
                vals.update({
                    'use_date': move_line.lot_use_date_name,
                })
        return super().create(vals)
