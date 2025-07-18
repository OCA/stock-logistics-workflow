# Copyright 2025 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare, float_round


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _split_move_line_package_qty(self, package_qty):
        """
        Split move line if the package quantity is less than the move line
        quantity.
        """
        self.ensure_one()
        if (
            float_compare(
                package_qty,
                self.quantity,
                precision_rounding=self.product_uom_id.rounding,
            )
            >= 0
        ):
            return False
        quantity_left_todo = float_round(
            self.quantity - package_qty,
            precision_rounding=self.product_uom_id.rounding,
            rounding_method="HALF-UP",
        )
        return self.copy(default={"quantity": quantity_left_todo})
