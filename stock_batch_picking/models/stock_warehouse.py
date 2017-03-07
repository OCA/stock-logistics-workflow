# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    default_picker_id = fields.Many2one(
        'res.users', 'Default Picker',
        help='the user to which the batch pickings are assigned by default',
        index=True,
    )
