# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_rate_ids = fields.One2many(
        string='Delivery Carrier Rates',
        comodel_name='delivery.carrier.rate',
        inverse_name='sale_order_id',
    )
