# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    volume = fields.Float(
        compute="_compute_volume",
        store=True,
    )
    volume_uom_name = fields.Char(
        string="Volume unit of measure label", compute="_compute_volume_uom_name"
    )

    def _compute_length_uom_name(self):
        self.length_uom_name = self.env[
            "product.template"
        ]._get_length_uom_name_from_ir_config_parameter()

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()

    @api.depends("packaging_length", "width", "height")
    def _compute_volume(self):
        conversion_uom_dict = {"mm³": 1, "cm³": 1000000, "m³": 1000000000}
        for rec in self:
            rec.volume = 0
            if rec.length_uom_name == "mm" and rec.volume_uom_name:
                rec.volume = (
                    rec.packaging_length * rec.width * rec.height
                ) / conversion_uom_dict[rec.volume_uom_name]
