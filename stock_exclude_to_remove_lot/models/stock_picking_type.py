# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    exclude_to_remove_lots = fields.Boolean(
        help="By default, lots with expired removal date can be selected"
             "in pickings."
             "Check this to restrict them."
    )
