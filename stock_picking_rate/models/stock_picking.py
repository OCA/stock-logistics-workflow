# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dispatch_rate_ids = fields.One2many(
        string='Dispatch Rates',
        comodel_name='stock.picking.rate',
        inverse_name='picking_id',
    )
