# Copyright 2025 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _split_move_line_package_qty(self, package_qty):
        """
        Split move line if the package quantity is less than the move line
        quantity.
        """
        self.ensure_one()
        if self.uom_id.compare(package_qty, self.quantity) >= 0:
            return False
        quantity_left_todo = self.uom_id.round(self.quantity - package_qty)
        return self.copy(default={"quantity": quantity_left_todo})
