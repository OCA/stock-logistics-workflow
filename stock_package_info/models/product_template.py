# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_net = fields.Float(
        string='Net Weight',
        help='Weight of product inside package',
        digits=dp.get_precision('Stock Weight'),
    )
