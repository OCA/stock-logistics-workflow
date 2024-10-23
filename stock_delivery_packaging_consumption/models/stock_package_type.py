from odoo import fields, models


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain="[('detailed_type', '=', 'product')]",
        inverse="_inverse_product_id",
        ondelete="set null",
        help="If set, a move line will be created and confirmed after "
        "a delivery containing this package is validated, "
        "in order to track the inventory level of this product",
    )

    def _inverse_product_id(self):
        """For convenience apply product weight to package type base weight"""
        for package_type in self:
            if (
                package_type.product_id
                and package_type.product_id.weight
                and not package_type.base_weight
            ):
                package_type.base_weight = package_type.product_id.weight
