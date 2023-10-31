# Copyright 2021-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_landed_cost_line_delivery_values(self, carrier, price_unit):
        return {
            "product_id": carrier.product_id.id,
            "name": carrier.name,
            "price_unit": price_unit,
            "split_method": carrier.split_method_landed_cost_line,
        }

    def _create_delivery_line(self, carrier, price_unit):
        res = super()._create_delivery_line(carrier=carrier, price_unit=price_unit)
        if carrier.create_landed_cost_line:
            vals = self._prepare_landed_cost_line_delivery_values(carrier, price_unit)
            for lc in self.landed_cost_ids:
                lc.cost_lines = [(0, 0, vals)]
        return res
