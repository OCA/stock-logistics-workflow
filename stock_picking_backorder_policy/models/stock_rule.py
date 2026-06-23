# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        # Copy the backorder policy from the procurement values onto the move,
        # for both the initial procurement and any chained one.
        move_fields = super()._get_custom_move_fields()
        move_fields.append("backorder_policy")
        return move_fields
