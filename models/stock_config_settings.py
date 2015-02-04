# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    group_lot_default_locked = fields.Boolean(
        string='Create lot in lock status',
        help='If checked, production lots will be created locked by default')
