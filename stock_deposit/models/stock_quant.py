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

    @api.multi
    def write(self, vals):
        if 'reservation_id' in vals:
            for quant in self:
                stock_move = self.env['stock.move'].browse(
                    vals['reservation_id'])
                if stock_move and stock_move.picking_id.owner_id:
                    vals['owner_id'] = stock_move.picking_id.owner_id.id
                elif quant.owner_id:
                    location_id = vals.get('location_id', False)
                    if not self.env['stock.location'].browse(
                            location_id).deposit_location:
                        # Remove owner only if the location to write is not a
                        # deposit location
                        vals['owner_id'] = False
        res = super(StockQuant, self).write(vals)
        return res
