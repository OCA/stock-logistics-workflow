# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_properties(self, move_line=False, move=False):
        res = super()._get_aggregated_properties(move_line=move_line, move=move)
        move = move or move_line.move_id
        if move.product_customer_code:
            res["name"] = move._get_report_product_display_name()
        return res
