# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    weight = fields.Float(
        related='product_id.weight',
        help='Weight of contents including package weight',
        digits=dp.get_precision('Stock Weight'),
    )
    weight_net = fields.Float(
        string='Net Weight',
        related='product_id.weight_net',
        help='Weight of contents excluding package weight',
        digits=dp.get_precision('Stock Weight'),
    )
    total_weight = fields.Float(
        store=True,
        compute='_compute_totals',
        digits=dp.get_precision('Stock Weight'),
    )
    total_weight_net = fields.Float(
        string='Total Net Weight',
        store=True,
        compute='_compute_totals',
        digits=dp.get_precision('Stock Weight'),
    )
    volume = fields.Float(
        related='product_id.volume',
        digits=dp.get_precision('Stock Weight'),
    )
    total_volume = fields.Float(
        store=True,
        compute='_compute_totals',
        digits=dp.get_precision('Stock Weight'),
    )

    @api.multi
    @api.depends('product_id', 'product_id.weight', 'qty',
                 'product_id.volume', 'product_id.weight_net')
    def _compute_totals(self):
        for rec in self:
            rec.total_weight = rec.product_id.weight * rec.qty
            rec.total_weight_net = rec.product_id.weight_net * rec.qty
            rec.total_volume = rec.product_id.volume * rec.qty
