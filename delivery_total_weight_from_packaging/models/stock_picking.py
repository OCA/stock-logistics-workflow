# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_bulk_weight(self):
        # Override method from `delivery` module to compute a more accurate
        # weight from the product packaging for bulk moves (without package)
        for picking in self:
            weight = 0.0
            for move_line in picking.move_line_ids:
                if move_line.product_id and not move_line.result_package_id:
                    weight += move_line.product_id.get_total_weight_from_packaging(
                        move_line.qty_done
                    )
            picking.weight_bulk = weight
