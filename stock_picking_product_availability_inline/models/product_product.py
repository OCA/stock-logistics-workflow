# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if self.env.context.get("sp_product_stock_inline"):
            dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
            new_res = []
            for product_id, display_name in res:
                product = self.env["product.product"].browse(product_id)
                new_res.append(
                    (
                        product_id,
                        f"{display_name} ({product.free_qty:.{dp}f}"
                        + f" {product.uom_id.name})",
                    )
                )
            res = new_res
        return res
