# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _block_deposit_quants(self, domain):
        domain.append(('location_id.deposit_location', '=', False))
        return domain

    @api.model
    def quants_get(self, qty, move, ops=False, domain=None,
                   removal_strategy='fifo'):
        if move.location_dest_id.deposit_location:
            domain = self._block_deposit_quants(domain)
        elif not move.location_id.deposit_location and \
                not move.location_dest_id.deposit_location:
            domain = self._block_deposit_quants(domain)
        return super(StockQuant, self).quants_get(
            qty, move, ops, domain, removal_strategy)
