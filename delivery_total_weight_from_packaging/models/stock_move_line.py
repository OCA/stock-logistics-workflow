# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_weight_from_packaging(self):
        """Return the line weight, including the weight of its packagings."""
        self.ensure_one()
        qty = self.product_uom_id._compute_quantity(
            self.quantity, self.product_id.uom_id
        )
        return self.product_id.get_total_weight_from_packaging(qty)
