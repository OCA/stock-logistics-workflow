# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):
        super(StockMove, self).product_price_update_before_done()
        for move in self.filtered(
                lambda move: move.location_id.usage == 'supplier' and
                move.product_id.cost_method == 'last'):
            company_id = move.company_id.id
            move.product_id.with_context(force_company=company_id).write(
                {'standard_price': move.get_price_unit()})
