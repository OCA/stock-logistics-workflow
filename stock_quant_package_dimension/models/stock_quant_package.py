# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    pack_weight = fields.Float()
    pack_length = fields.Integer(help="length")
    width = fields.Integer("Pack Width", help="width")
    height = fields.Integer("Pack Height", help="height")
    volume = fields.Float(
        "Pack Volume",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        help="volume",
    )
    estimated_pack_weight_kg = fields.Float(
        "Estimated weight (in kg)",
        digits="Product Unit of Measure",
        compute="_compute_estimated_pack_weight_kg",
        help="Based on the weight of the product.",
    )

    length_uom_id = fields.Many2one(
        # Same as product.packing
        "uom.uom",
        "Dimensions Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.uom_categ_length").id)
        ],
        help="UoM for pack length, height, width (based on lenght UoM)",
        default=lambda self: self.env[
            "product.template"
        ]._get_length_uom_id_from_ir_config_parameter(),
    )
    length_uom_name = fields.Char(
        # Same as product.packing
        string="Length unit of measure label",
        related="length_uom_id.name",
        readonly=True,
    )

    weight_uom_id = fields.Many2one(
        # Same as product.packing
        "uom.uom",
        string="Weight Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
        help="Weight Unit of Measure",
        compute=False,
        default=lambda self: self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter(),
    )

    weight_uom_name = fields.Char(
        # Same as product.packing
        string="Weight unit of measure label",
        compute="_compute_weight_uom_name",
    )

    volume_uom_id = fields.Many2one(
        # Same as product.packing
        "uom.uom",
        string="Volume Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)
        ],
        help="Packaging volume unit of measure",
        default=lambda self: self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter(),
    )

    volume_uom_name = fields.Char(
        # Same as product.packing
        string="Volume Unit of Measure label",
        related="volume_uom_id.name",
        readonly=True,
    )

    @api.depends("weight_uom_id", "weight_uom_id.name")
    def _compute_weight_uom_name(self):
        # Don't use a related here as the original default value
        # causes warnings (Redundant default on related fields are not wanted)
        for package in self:
            package.weight_uom_name = package.weight_uom_id.name

    @api.depends("pack_length", "width", "height")
    def _compute_volume(self):
        Packaging = self.env["product.packaging"]
        for pack in self:
            pack.volume = Packaging._calculate_volume(
                pack.pack_length,
                pack.height,
                pack.width,
                pack.length_uom_id,
                pack.volume_uom_id,
            )

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
            "packaging_length": "pack_length",
            "width": "width",
            "height": "height",
            "weight": "pack_weight",
            "length_uom_id": "length_uom_id",
            "weight_uom_id": "weight_uom_id",
            "volume_uom_id": "volume_uom_id",
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

    def _get_weight_kg_from_move_lines(self, move_lines):
        uom_kg = self.env.ref("uom.product_uom_kgm")
        return sum(
            ml.product_uom_id._compute_quantity(
                qty=ml.quantity, to_unit=ml.product_id.uom_id
            )
            * ml.product_id.weight_uom_id._compute_quantity(
                qty=ml.product_id.weight, to_unit=uom_kg
            )
            for ml in move_lines
        )

    def _get_weight_kg_from_quants(self, quants):
        uom_kg = self.env.ref("uom.product_uom_kgm")
        return sum(
            quant.quantity
            * quant.product_id.weight_uom_id._compute_quantity(
                qty=quant.product_id.weight, to_unit=uom_kg
            )
            for quant in quants
        )

    @api.depends("quant_ids")
    @api.depends_context("picking_id")
    def _compute_estimated_pack_weight_kg(self):
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
                weight = package._get_weight_kg_from_move_lines(move_lines)
            else:
                weight = package._get_weight_kg_from_quants(package.quant_ids)
            package.estimated_pack_weight_kg = weight
