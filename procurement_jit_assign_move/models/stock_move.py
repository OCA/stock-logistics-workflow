# -*- coding: utf-8 -*-
# © 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_confirm(self):
        res = super(StockMove, self).action_confirm()
        make_to_stock_moves = self.filtered(
            lambda x: x.procure_method == 'make_to_stock'
        )
        make_to_stock_moves.action_assign()
        return res
