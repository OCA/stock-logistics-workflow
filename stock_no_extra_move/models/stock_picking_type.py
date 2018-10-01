# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    allow_process_qty = fields.Boolean(
        string='Allow process quantities',
    )
