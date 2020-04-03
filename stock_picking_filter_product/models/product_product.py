# Copyright 2020 Alan Ramos - Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    location_ids = fields.Many2many(
        string='Locations', comodel_name='stock.location',
        compute='_compute_location_ids', store=True)

    @api.depends('stock_quant_ids', 'stock_quant_ids.location_id')
    def _compute_location_ids(self):
        for product in self:
            product.location_ids = product.mapped(
                'stock_quant_ids.location_id')
