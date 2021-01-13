# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    pack_weight = fields.Float("Weight (kg)")
    estimated_pack_weight = fields.Float(
        "Estimated weight (kg)",
        digits="Product Unit of Measure",
        compute="_compute_estimated_pack_weight",
        help="Based on the weight of the product.",
    )
    # lngth IS NOT A TYPO: https://github.com/odoo/odoo/issues/41353
    lngth = fields.Integer("Length (mm)", help="length in millimeters")
    width = fields.Integer("Width (mm)", help="width in millimeters")
    height = fields.Integer("Height (mm)", help="height in millimeters")
    volume = fields.Float(
        "Volume (m³)",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        help="volume in cubic meters",
    )

    def _get_picking_move_line_ids_per_package(self, picking_id):
        if not picking_id:
            return {}
        move_lines = self.env["stock.move.line"].search(
            [("result_package_id", "in", self.ids), ("picking_id", "=", picking_id)]
        )
        res = dict.fromkeys(self.ids, self.env["stock.move.line"])
        for ml in move_lines:
            res.setdefault(ml.result_package_id, set(ml.ids))
            res[ml.result_package_id].add(ml.id)
        return res

    def _get_weight_from_move_lines(self, move_lines):
        return sum(
            ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
            * ml.product_id.weight
            for ml in move_lines
        )

    def _get_weight_from_quants(self, quants):
        return sum(quant.quantity * quant.product_id.weight for quant in quants)

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_estimated_pack_weight(self):
        # NOTE: copy-pasted and adapted from `delivery` module
        # because we do not want to add the dependency against 'delivery' here.
        picking_id = self.env.context.get("picking_id")
        move_line_ids_per_package = self._get_picking_move_line_ids_per_package(
            picking_id
        )
        for package in self:
            weight = 0.0
            if picking_id:  # coming from a transfer
                move_line_ids = move_line_ids_per_package.get(package, [])
                move_lines = self.env["stock.move.line"].browse(move_line_ids)
                weight = package._get_weight_from_move_lines(move_lines)
            else:
                weight = package._get_weight_from_quants(package.quant_ids)
            package.estimated_pack_weight = weight

    @api.depends("lngth", "width", "height")
    def _compute_volume(self):
        for pack in self:
            pack.volume = (pack.lngth * pack.width * pack.height) / 1000.0 ** 3

    def auto_assign_packaging(self):
        self = self.with_context(_auto_assign_packaging=True)
        res = super().auto_assign_packaging()
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("_auto_assign_packaging") and vals.get(
            "product_packaging_id"
        ):
            self._update_dimensions_from_packaging(override=False)
        return res

    def _update_dimensions_fields(self):
        # source: destination
        return {
            "lngth": "lngth",
            "width": "width",
            "height": "height",
            "max_weight": "pack_weight",
        }

    def _update_dimensions_from_packaging(self, override=False):
        for package in self:
            if not package.product_packaging_id:
                continue
            dimension_fields = self._update_dimensions_fields()
            for source, dest in dimension_fields.items():
                if not override and package[dest]:
                    continue
                package[dest] = package.product_packaging_id[source]

    @api.onchange("product_packaging_id")
    def onchange_product_packaging_id(self):
        self._update_dimensions_from_packaging(override=True)
