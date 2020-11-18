# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from odoo import api, fields, models


class StockLocationPath(models.Model):

    _inherit = 'stock.location.path'

    auto_move = fields.Boolean(
        help="If this option is selected, the generated moves will be "
             "automatically processed as soon as the products are available. "
             "This can be useful for situations with chained moves where we "
             "do not want an operator action.",
        oldname="auto_confirm",
    )

    @api.model
    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super(StockLocationPath, self)._prepare_move_copy_values(
            move_to_copy=move_to_copy, new_date=new_date)
        new_move_vals.update({'auto_move': self.auto_move})
        return new_move_vals
