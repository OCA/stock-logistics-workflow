# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    # This fiels already exists and it's stored.
    # Here is made computed but kept editable using readonly=False
    shipping_weight = fields.Float(
        compute="_compute_shipping_weight", readonly=False, store=True
    )

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_weight(self):
        # Override method from `delivery` module to compute a more accurate
        # weight by including the weight of the packaging
        for package in self:
            package.weight = package._get_weight_from_packaging()

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_shipping_weight(self):
        for package in self:
            package.shipping_weight = package._get_weight_from_packaging()

    def _get_weight_from_packaging(self):
        # NOTE: code copied/pasted and adapter from `delivery`
        weight = 0.0
        if self.env.context.get("picking_id"):
            current_picking_move_line_ids = self.env["stock.move.line"].search(
                [
                    ("result_package_id", "=", self.id),
                    ("picking_id", "=", self.env.context["picking_id"]),
                ]
            )
            for ml in current_picking_move_line_ids:
                weight += ml.product_id.get_total_weight_from_packaging(ml.qty_done)
        else:
            for quant in self.quant_ids:
                weight += quant.product_id.get_total_weight_from_packaging(
                    quant.quantity
                )
        return weight
