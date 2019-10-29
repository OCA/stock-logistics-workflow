# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_cost_history_date(self, date):
        return self.env['product.price.history'].search([
            ('product_id', '=', self.id),
            ('datetime', '<', date),
        ], limit=1, order='datetime DESC').cost
