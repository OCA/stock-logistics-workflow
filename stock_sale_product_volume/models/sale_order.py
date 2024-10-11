# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_volume = fields.Float(
        compute="_compute_total_volume", string="Volume in cubic meter"
    )
    volume_uom_name = fields.Char(
        string="Volume unit of measure label", compute="_compute_volume_uom_name"
    )

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()

    def _compute_total_volume(self):
        for record in self:
            total_volume = 0
            for order_line in record.order_line:
                total_volume += (
                    order_line.product_packaging_id.package_type_id.volume
                    * order_line.product_packaging_qty
                )
            record.total_volume = total_volume if total_volume > 0 else 0
