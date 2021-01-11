# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    pack_weight = fields.Float("Weight")
    pack_length = fields.Integer("Length", help="length")
    width = fields.Integer("Width", help="width")
    height = fields.Integer("Height", help="height")
    volume = fields.Float(
        "Volume",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        help="volume",
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
        related="weight_uom_id.name",
        readonly=True,
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
            "max_weight": "pack_weight",
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
