# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_weight(self):
        # Override method from `delivery` module to compute a more accurate
        # weight by including the weight of the packaging
        # NOTE: code copied/pasted and adapter from `delivery`
        for package in self:
            weight = 0.0
            if self.env.context.get("picking_id"):
                current_picking_move_line_ids = self.env["stock.move.line"].search(
                    [
                        ("result_package_id", "=", package.id),
                        ("picking_id", "=", self.env.context["picking_id"]),
                    ]
                )
                for ml in current_picking_move_line_ids:
                    weight += ml.product_id.get_total_weight_from_packaging(ml.qty_done)
            else:
                for quant in package.quant_ids:
                    weight += quant.product_id.get_total_weight_from_packaging(
                        quant.quantity
                    )
            package.weight = weight
