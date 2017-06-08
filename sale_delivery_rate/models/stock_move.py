# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_confirm(self):
        """Overloaded to generate picking rates based on a picking's sale
        order. Pickings are connected to sale orders through moves and this
        action is where moves and pickings are typically joined.
        """
        result = super(StockMove, self).action_confirm()

        updated_pickings = self.mapped('picking_id')
        for picking in updated_pickings:
            if picking.dispatch_rate_ids:
                continue

            if picking.sale_id and picking.sale_id.carrier_id:
                matching_rate = self.env['delivery.carrier.rate'].search([
                    ('sale_order_id', '=', picking.sale_id.id),
                    ('service_id', '=', picking.sale_id.carrier_id.id),
                ])
                matching_rate.generate_equiv_picking_rates(picking)

        return result
