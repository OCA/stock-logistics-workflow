# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    estimated_pack_weight_kg = fields.Float(
        # Overloaded field
        help="Based on the weight of the product packagings."
    )

    def _get_weight_kg_from_move_lines(self, move_lines):
        # Overridden from 'stock_quant_package_dimension' module to use the
        # 'get_total_weight_from_packaging' method supplied by the
        # 'product_total_weight_from_packaging' module
        return sum(
            ml.product_id.get_total_weight_from_packaging(ml.qty_done)
            for ml in move_lines
        )

    def _get_weight_kg_from_quants(self, quants):
        # Overridden from 'stock_quant_package_dimension' module to use the
        # 'get_total_weight_from_packaging' method supplied by the
        # 'product_total_weight_from_packaging' module
        return sum(
            quant.product_id.get_total_weight_from_packaging(quant.quantity)
            for quant in quants
        )
