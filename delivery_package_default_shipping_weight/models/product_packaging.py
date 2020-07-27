# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    package_default_shipping_weight = fields.Float(
        string="Default shipping weight",
        help="If set, this weight will be used as default value for Shipping "
        "weight, when this Package Type is selected on a Package.",
    )

    @api.constrains("package_default_shipping_weight")
    def _check_package_default_shipping_weight(self):
        weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()
        for packaging in self:
            if (
                float_compare(
                    packaging.package_default_shipping_weight,
                    0,
                    precision_rounding=weight_uom.rounding,
                )
                < 0
            ):
                raise ValidationError(
                    _("Default shipping weight must be a positive or null value.")
                )
