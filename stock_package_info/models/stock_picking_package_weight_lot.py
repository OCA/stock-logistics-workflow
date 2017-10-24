# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class StockPickingPackageWeightLot(models.Model):
    _name = 'stock.picking.package.weight.lot'
    _description = 'Stock Picking Package Weight Total'
    _order = 'sequence'

    sequence = fields.Integer()
    package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Package',
    )
    lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        string='Lots/Serial Numbers',
    )
    net_weight = fields.Float(
        digits=dp.get_precision('Stock Weight'),
    )
    gross_weight = fields.Float(
        digits=dp.get_precision('Stock Weight'),
    )
