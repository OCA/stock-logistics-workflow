# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_elaboration_stock_route(self):
        # Deposit lines won't be elaborated
        if (
            self.warehouse_id.use_customer_deposits
            and self.product_id.is_storable
            and self.order_id.customer_deposit
        ):
            return
        return super().get_elaboration_stock_route()
