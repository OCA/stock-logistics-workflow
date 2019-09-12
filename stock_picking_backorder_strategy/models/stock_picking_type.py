# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    backorder_strategy = fields.Selection(
        [('manual', 'Manual'), ('create', 'Create'),
         ('no_create', 'No create'),
         ('cancel', 'Cancel')],
        default='manual',
        help="Define what to do with backorder",
        required=True
    )
