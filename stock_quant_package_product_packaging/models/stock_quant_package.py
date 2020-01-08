# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    # This is not the same thing as 'packaging_id':
    # * packaging_id is the "Package type", packaging which have
    #   no 'product_id' and used for the delivery (postal 2kg, ...)
    # * product_packaging_id is the actual Product Packaging (usually
    #   using a GTIN) used for the internal logistics/reception. It
    #   has a product_id
    product_packaging_id = fields.Many2one(
        "product.packaging",
        "Product Packaging",
        index=True,
        help="Packaging of the product, used for internal logistics"
        "transfers, put-away rules, ...",
    )
    single_product_id = fields.Many2one(
        "product.product", compute="_compute_single_product"
    )
    single_product_qty = fields.Float(compute="_compute_single_product")

    @api.depends("quant_ids", "quant_ids.product_id")
    def _compute_single_product(self):
        for pack in self:
            pack_products = pack.quant_ids.mapped("product_id")
            if len(pack_products) == 1:
                pack.single_product_id = pack_products.id
                # TODO handle uom
                pack.single_product_qty = sum(pack.quant_ids.mapped("quantity"))
            else:
                pack.single_product_id = False
                pack.single_product_qty = 0

    def auto_assign_packaging(self):
        for pack in self:
            if (
                not pack.product_packaging_id
                and pack.single_product_id
                and pack.single_product_qty
            ):
                packaging = self.env["product.packaging"].search(
                    [
                        ("product_id", "=", pack.single_product_id.id),
                        ("qty", "=", pack.single_product_qty),
                    ],
                    limit=1,
                )
                if packaging:
                    pack.write({"product_packaging_id": packaging.id})
