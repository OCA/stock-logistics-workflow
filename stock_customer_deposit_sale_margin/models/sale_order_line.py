# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("deposit_available_qty", "product_uom_qty")
    def _compute_purchase_price(self):
        # When the deposit is enough to deliver the demand, set purchase price to zero
        # as it was already sold in the original deposit order.
        res = super()._compute_purchase_price()
        self.filtered(
            lambda x: x.product_uom
            and float_compare(
                x.deposit_available_qty,
                x.product_uom_qty,
                precision_rounding=x.product_uom.rounding,
            )
            >= 0
        ).purchase_price = 0
        return res
