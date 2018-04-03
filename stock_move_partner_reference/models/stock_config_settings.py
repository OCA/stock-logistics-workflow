# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockConfigSettings(models.TransientModel):

    _inherit = 'stock.config.settings'

    group_stock_use_partner_move_reference = fields.Selection([
        (0, 'Do not use partner reference in stock moves'),
        (1, 'Track partner reference in stock moves')
    ], "Partner Reference",
        implied_group='stock_move_partner_reference.'
                      'group_stock_use_partner_move_reference',
        help="""This allows you to assign a partner reference in stock moves
         to help delivery or reception"""
    )
