# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    filter_location_id = fields.Many2one(
        comodel_name='stock.location',
        default=lambda self: self.env.ref('stock.stock_location_stock'))
