# ?? 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    allow_negative_stock = fields.Boolean(
        string="Allow Negative Stock",
        help="Allow negative stock levels for the stockable products "
        "attached to this category. The options doesn't apply to products "
        "attached to sub-categories of this category.",
    )

    @api.constrains("allow_negative_stock")
    def _check_allow_negative_stock(self):
        for rec in self:
            if not rec.allow_negative_stock:
                self.env["stock.quant"].search(
                    [("product_id.categ_id", "=", rec.id)]
                ).check_negative_qty()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        string="Allow Negative Stock",
        help="If this option is not active on this product nor on its "
        "product category and that this product is a stockable product, "
        "then the validation of the related stock moves will be blocked if "
        "the stock level becomes negative with the stock move.",
    )

    @api.constrains("allow_negative_stock", "categ_id")
    def _check_allow_negative_stock(self):
        for rec in self:
            if not rec.allow_negative_stock:
                self.env["stock.quant"].search(
                    [
                        (
                            "product_id",
                            "in",
                            rec.with_context(active_test=False).product_variant_ids.ids,
                        )
                    ]
                ).check_negative_qty()
