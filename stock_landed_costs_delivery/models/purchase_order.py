# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_landed_cost_line_delivery_values(self):
        return {
            "product_id": self.carrier_id.product_id.id,
            "name": self.carrier_id.name,
            "price_unit": self.delivery_price,
            "split_method": self.carrier_id.split_method_landed_cost_line,
        }

    def _prepare_landed_cost_values(self, picking):
        res = super()._prepare_landed_cost_values(picking)
        if self.carrier_id.create_landed_cost_line:
            res.setdefault("cost_lines", [])
            res["cost_lines"].append(
                (0, 0, self._prepare_landed_cost_line_delivery_values())
            )
        return res
