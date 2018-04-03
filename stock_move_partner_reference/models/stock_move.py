# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    partner_reference = fields.Char(
        copy=False,
        index=True,
    )
