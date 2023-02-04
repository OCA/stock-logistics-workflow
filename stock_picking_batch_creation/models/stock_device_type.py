# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockDeviceType(models.Model):

    _name = "stock.device.type"
    _description = "Stock Device Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    min_volume = fields.Float(
        string="Minimum total net volume for this device",
        help="Volume in default system volume unit of measure",
    )
    max_volume = fields.Float(
        string="Maximum total net volume for this device",
        help="Volume in default system volume unit of measure",
    )
    max_weight = fields.Float(
        string="Maximum total net weight for this device",
        help="Weight in default system weight unit of measure",
    )
    user_min_volume = fields.Float(
        string="Minimum total net volume for electing this device",
        compute="_compute_user_min_volume",
        inverse="_inverse_user_min_volume",
        readonly=False,
    )
    user_max_volume = fields.Float(
        string="Maximum total net volume for electing this device",
        compute="_compute_user_max_volume",
        inverse="_inverse_user_max_volume",
        readonly=False,
    )
    user_max_weight = fields.Float(
        string="Maximum total net weight for electing this device",
        compute="_compute_user_max_weight",
        inverse="_inverse_user_max_weight",
        readonly=False,
    )
    nbr_bins = fields.Integer(string="Number of compartments")

    volume_per_bin = fields.Float(
        string="Max volume per bin", compute="_compute_volume_per_bin"
    )
    user_weight_uom_id = fields.Many2one(
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

    user_weight_uom_name = fields.Char(
        # Same as product.packing
        string="Weight unit of measure label",
        related="user_weight_uom_id.display_name",
        readonly=True,
    )

    user_volume_uom_id = fields.Many2one(
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
        required=True,
    )

    user_volume_uom_name = fields.Char(
        # Same as product.packing
        string="Volume Unit of Measure label",
        related="user_volume_uom_id.display_name",
        readonly=True,
        required=True,
    )

    sequence = fields.Integer(string="Priority")

    @api.depends("max_volume", "nbr_bins")
    def _compute_volume_per_bin(self):
        for rec in self:
            vol = 0
            if rec.max_volume and rec.nbr_bins:
                vol = rec.max_volume / rec.nbr_bins
            rec.volume_per_bin = vol

    @api.model
    def _get_system_volume_uom(self):
        return self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()

    @api.model
    def _get_system_weight_uom(self):
        return self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

    @api.depends("max_volume", "user_volume_uom_id")
    def _compute_user_max_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            if rec.max_volume:
                rec.user_max_volume = volume_uom._compute_quantity(
                    rec.max_volume, to_unit=rec.user_volume_uom_id
                )
            else:
                rec.user_max_volume = 0

    def _inverse_user_max_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            if rec.user_max_volume:
                rec.max_volume = rec.user_volume_uom_id._compute_quantity(
                    rec.user_max_volume, to_unit=volume_uom
                )
            else:
                rec.max_volume = 0

    @api.depends("min_volume", "user_volume_uom_id")
    def _compute_user_min_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            if rec.min_volume:
                rec.user_min_volume = volume_uom._compute_quantity(
                    rec.min_volume, to_unit=rec.user_volume_uom_id
                )
            else:
                rec.user_min_volume = 0

    def _inverse_user_min_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            if rec.user_min_volume:
                rec.min_volume = rec.user_volume_uom_id._compute_quantity(
                    rec.user_min_volume, to_unit=volume_uom
                )
            else:
                rec.min_volume = 0

    @api.depends("max_weight", "user_weight_uom_id")
    def _compute_user_max_weight(self):
        weight_uom = self._get_system_weight_uom()
        for rec in self:
            if rec.max_weight:
                rec.user_max_weight = weight_uom._compute_quantity(
                    rec.max_weight, to_unit=rec.user_weight_uom_id
                )
            else:
                rec.user_max_weight = 0

    def _inverse_user_max_weight(self):
        weight_uom = self._get_system_weight_uom()
        for rec in self:
            if rec.user_max_weight:
                rec.max_weight = rec.user_weight_uom_id._compute_quantity(
                    rec.user_max_weight, to_unit=weight_uom
                )
            else:
                rec.max_weight = 0
