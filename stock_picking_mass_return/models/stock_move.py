# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def get_available_quantity_to_return(self):
        quant_obj = self.env['stock.quant']

        self.ensure_one()
        quants = quant_obj.search([
            ('history_ids', 'in', [self.id]),
            ('qty', '>', 0.0),
            ('location_id', 'child_of', self.location_dest_id.id),
        ])
        quants_to_process = quants.filtered(
            lambda quant: not quant.reservation_id or
            quant.reservation_id.origin_returned_move_id.id != self.id)
        quantity = sum(quant.qty for quant in quants_to_process)
        quantity = self.product_id.uom_id._compute_quantity(
            quantity, self.product_uom)

        return quantity
