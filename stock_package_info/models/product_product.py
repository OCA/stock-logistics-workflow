# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight_net = fields.Float(
        string='Net Weight',
        help='Weight of contents excluding package weight',
        digits=dp.get_precision('Stock Weight'),
    )
