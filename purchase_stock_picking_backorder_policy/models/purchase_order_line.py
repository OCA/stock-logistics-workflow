# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        # Seed the backorder policy from the order onto the moves, so it keeps
        # operations with a different policy in their own receipt and follows
        # any downstream (push) step.
        vals_list = super()._prepare_stock_moves(picking)
        for vals in vals_list:
            vals["backorder_policy"] = self.order_id.backorder_policy
        return vals_list
