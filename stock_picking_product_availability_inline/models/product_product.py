# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        res = super().name_get()
        if self.env.context.get("sp_product_stock_inline"):
            product_dict = {r.id: r for r in self}
            dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
            new_res = []
            for rec_name in res:
                prod = product_dict[rec_name[0]]
                name = f"{rec_name[1]} ({prod.free_qty:.{dp}f} {prod.uom_id.name})"
                new_res.append((prod.id, name))
            res = new_res
        return res
