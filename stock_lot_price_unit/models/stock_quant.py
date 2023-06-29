# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    price_unit = fields.Float(
        "Reference Price",
        compute="_compute_price_unit",
    )
    amount = fields.Monetary(
        "Reference Amount",
        compute="_compute_price_unit",
    )

    def _compute_price_unit(self):
        for quant in self:
            if quant.lot_id:
                quant.price_unit = quant.lot_id.price_unit
            else:
                quant.price_unit = quant.product_id.with_company(
                    quant.company_id
                ).avg_cost
            quant.amount = quant.quantity * quant.price_unit
