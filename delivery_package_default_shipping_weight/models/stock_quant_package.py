# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.onchange("packaging_id")
    def _onchange_packaging_id(self):
        if self.packaging_id and self.packaging_id.package_default_shipping_weight:
            self.shipping_weight = self.packaging_id.package_default_shipping_weight

    @api.model
    def _update_vals_for_shipping_weight(self, vals):
        package_type_id = vals.get("packaging_id")
        if package_type_id and not vals.get("shipping_weight"):
            packaging = self.env["product.packaging"].browse(package_type_id)
            if packaging.package_default_shipping_weight:
                vals["shipping_weight"] = packaging.package_default_shipping_weight
        return vals

    @api.model
    def create(self, vals):
        vals = self._update_vals_for_shipping_weight(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self._update_vals_for_shipping_weight(vals)
        return super().write(vals)
