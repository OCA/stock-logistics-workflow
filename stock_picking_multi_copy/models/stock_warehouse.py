# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import models, fields, api
from odoo import http


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    deliveryslip_folder = fields.Char(
        string='Delivery Slip Folder',
        help='Directory where to store Delivery Slip report')
