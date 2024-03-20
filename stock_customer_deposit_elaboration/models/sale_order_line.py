# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    route_id = fields.Many2one(
        "stock.route", compute="_compute_route_id", store=True, readonly=False
    )

    @api.depends(
        "product_id",
        "warehouse_id.use_customer_deposits",
        "order_id.customer_deposit",
        "elaboration_ids",
    )
    def _compute_route_id(self):
        for line in self:
            line.route_id = line._get_stock_route()

    def _get_stock_route(self):
        self.ensure_one()
        if (
            self.warehouse_id.use_customer_deposits
            and self.product_id.type == "product"
            and self.order_id.customer_deposit
        ):
            return self.warehouse_id.customer_deposit_route_id
        return self.elaboration_ids.route_ids[:1]
