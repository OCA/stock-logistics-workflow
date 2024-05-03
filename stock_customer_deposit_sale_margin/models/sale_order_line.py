# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id",
        "company_id",
        "currency_id",
        "product_uom",
        "deposit_available_qty",
        "product_uom_qty",
    )
    def _compute_purchase_price(self):
        res = super()._compute_purchase_price()
        for line in self:
            if 0 <= line.deposit_available_qty <= line.product_uom_qty:
                continue
            # Set purchase price to zero because purchase price is in sale order
            # that made customer deposit, otherwise the cost would be posted twice.
            line.purchase_price = 0.0
        return res
