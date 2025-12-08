# Copyright 2021 Camptocamp SA
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    # This fiels already exists and it's stored.
    # Here is made computed but kept editable using readonly=False
    shipping_weight = fields.Float(
        compute="_compute_shipping_weight", readonly=False, store=True
    )

    def _get_weight(self, picking_id=False):
        """
        Override standard method to use custom packaging weight logic.
        """
        res = {}
        for package in self:
            res[package] = package._get_weight_from_packaging(picking_id)
        return res

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_shipping_weight(self):
        for package in self:
            # When you ship the parcel, the weight should not be erased and
            # remain the one that was encoded during the packing step.
            package.shipping_weight = (
                package.shipping_weight
                or package._get_weight_from_packaging(
                    self.env.context.get("picking_id")
                )
            )

    def _get_weight_from_packaging(self, picking_id=None):
        # NOTE: code copied/pasted and adapter from `delivery`
        weight = 0.0
        if picking_id:
            current_picking_move_line_ids = self.env["stock.move.line"].search(
                [
                    ("result_package_id", "=", self.id),
                    ("picking_id", "=", picking_id),
                ]
            )
            for ml in current_picking_move_line_ids:
                weight += ml.product_id.get_total_weight_from_packaging(ml.quantity)
        else:
            for quant in self.quant_ids:
                weight += quant.product_id.get_total_weight_from_packaging(
                    quant.quantity
                )
        return weight
