# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    def _check_rule(self):
        return (
            self.cost_line_id.product_id.product_tmpl_id.id
            in self.product_id.product_tmpl_landed_cost_ids.ids
            and self.product_id.landed_cost_specific
        ) or not self.product_id.landed_cost_specific
