# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    cannabis_test_id = fields.Many2one(
        string='Cannabis Test',
        comodel_name='cannabis.test',
    )
    date_harvest = fields.Datetime(
        string='Harvest Date',
        default=lambda s: fields.Datetime.now(),
    )
    date_production = fields.Datetime(
        string='Production Date',
    )
    date_use = fields.Datetime(
        string='Use By Date',
    )
