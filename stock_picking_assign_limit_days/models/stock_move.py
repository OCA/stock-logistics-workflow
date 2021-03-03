# Copyright 2020 PlanetaTIC <info@planetatic.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        param_obj = self.env['ir.config_parameter']

        move_to_assign = self.browse()
        for move in self:
            if move.date_expected:
                confirm_before_days = param_obj.sudo().get_param(
                    'stock_picking_assign_limit_days.'
                    'stock_picking_assign_limit_days') or 0
                if confirm_before_days:
                    limit_date_to_assign = datetime.now() + relativedelta(
                        days=int(confirm_before_days))
                    if move.date_expected <= limit_date_to_assign:
                        move_to_assign |= move
        res = super(StockMove, move_to_assign)._action_assign()
        return res
