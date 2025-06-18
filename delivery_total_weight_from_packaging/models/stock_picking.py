# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_bulk_weight(self):
        # Override method from `stock` module to compute a more accurate
        # weight from the product packaging for bulk moves (without package)
        for picking in self:
            weight = 0.0
            for move_line in picking.move_line_ids:
                if move_line.product_id and not move_line.result_package_id:
                    weight += move_line.product_id.get_total_weight_from_packaging(
                        move_line.quantity
                    )
            picking.weight_bulk = weight

    def _get_estimated_weight(self):
        """Override to calculate the estimated total weight of all
        move lines in the record using product packaging."""
        self.ensure_one()
        weight = 0.0
        for move_line in self.move_line_ids:
            if move_line.product_id:
                weight += move_line.product_id.get_total_weight_from_packaging(
                    move_line.quantity
                )
        return weight
