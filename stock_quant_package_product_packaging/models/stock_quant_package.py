# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    single_product_id = fields.Many2one(
        'product.product', compute='_compute_single_product'
    )
    single_product_qty = fields.Float(compute='_compute_single_product')

    @api.depends('quant_ids', 'quant_ids.product_id')
    def _compute_single_product(self):
        for pack in self:
            pack_products = pack.quant_ids.mapped('product_id')
            if len(pack_products) == 1:
                pack.single_product_id = pack_products.id
                # TODO handle uom
                pack.single_product_qty = sum(pack.quant_ids.mapped('quantity'))
            else:
                pack.single_product_id = False
                pack.single_product_qty = 0

    def auto_assign_packaging(self):
        for pack in self:
            if (
                not pack.packaging_id
                and pack.single_product_id
                and pack.single_product_qty
            ):
                packaging = self.env['product.packaging'].search(
                    [
                        ('product_id', '=', pack.single_product_id.id),
                        ('qty', '=', pack.single_product_qty)
                    ], limit=1
                )
                if packaging:
                    pack.write({'packaging_id': packaging.id})
