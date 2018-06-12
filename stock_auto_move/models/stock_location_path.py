# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from openerp import api, fields, models


class StockLocationPath(models.Model):

    _inherit = 'stock.location.path'

    auto_confirm = fields.Boolean(
        help="If this option is selected, the generated moves will be "
             "automatically processed as soon as the products are available. "
             "This can be useful for situations with chained moves where we "
             "do not want an operator action."
    )

    @api.model
    def _prepare_push_apply(self, rule, move):
        new_move_vals = super(StockLocationPath, self)._prepare_push_apply(
            rule, move)
        new_move_vals.update({'auto_move': rule.auto_confirm})
        return new_move_vals
