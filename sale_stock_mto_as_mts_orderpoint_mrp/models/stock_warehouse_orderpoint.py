# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.constrains("product_id")
    def check_product_is_not_kit(self):
        # Bypasses the check regarding having orderpoints for phantom bom products
        # in `mrp`
        return True
