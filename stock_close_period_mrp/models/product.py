from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_product_order(self, product_order=None):
        if product_order is None:
            product_order = {}
        for product in self:
            bom = self.env["mrp.bom"].sudo()._bom_find(product)
            if bom:
                if any(x.child_bom_id for x in bom.bom_line_ids):
                    for child_bom_product in bom.bom_line_ids.filtered(
                        lambda line: line.child_bom_id
                    ).mapped("product_id"):
                        product_order = child_bom_product._get_product_order(
                            product_order=product_order
                        )
                if product.id not in product_order:
                    sequence = (max(product_order.values() or [0])) + 1
                    product_order.update({product.id: sequence})
            if product.id not in product_order:
                sequence = (max(product_order.values() or [0])) + 1
                product_order.update({product.id: sequence})
        return product_order

    def _get_extra_cost(self, bom):
        # overridable method
        return 0
