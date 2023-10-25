# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _update_valuation_backdating(self):
        for valuation in self.stock_valuation_layer_ids:
            accounting_date = self.account_move_id.date
            if accounting_date:
                self.env.cr.execute(
                    """UPDATE stock_valuation_layer SET create_date = %s WHERE id = %s""",
                    (accounting_date, valuation.id),
                )
                valuation.invalidate_cache()

    def button_validate(self):
        res = super().button_validate()
        if self.stock_valuation_layer_ids:
            self._update_valuation_backdating()
        return res
