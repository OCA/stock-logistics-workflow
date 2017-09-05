# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from openerp import api, models


class StockLocationPath(models.Model):

    _inherit = 'stock.location.path'

    @api.model
    def _apply(self, rule, move):
        """Set auto move to the new move created by push rule."""
        move.auto_move = rule.auto == 'transparent'
        return super(StockLocationPath, self)._apply(rule, move)
