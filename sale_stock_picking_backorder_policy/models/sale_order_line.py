# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self):
        # Seed the backorder policy from the order so it propagates down to the
        # pickings created from this line.
        values = super()._prepare_procurement_values()
        values["backorder_policy"] = self.order_id.backorder_policy
        return values
