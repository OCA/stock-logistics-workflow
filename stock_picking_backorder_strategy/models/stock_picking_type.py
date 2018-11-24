# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    backorder_strategy = fields.Selection(
        [('manual', _('Manual')), ('create', _('Create')),
         ('no_create', _('No create')),
         ('cancel', _('Cancel'))],
        default='manual',
        help="Define what to do with backorder",
        required=True
    )
