# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('base_on_rate', 'Based on Rates')],
    )

    @api.model
    def base_on_rate_get_shipping_price_from_so(self, sale_orders):
        prices = []

        for sale_order in sale_orders:
            order_rate = self.env['delivery.carrier.rate'].search([
                ('sale_order_id', '=', sale_order.id),
                ('service_id', '=', sale_order.carrier_id.id),
            ])

            if not order_rate:
                prices.append(0.0)
            elif order_rate.retail_rate:
                prices.append(order_rate.retail_rate)
            else:
                prices.append(order_rate.rate)

        return prices
