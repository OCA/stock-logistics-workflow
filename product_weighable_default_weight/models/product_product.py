# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("uom_id", "uom_po_id")
    def _onchange_uom(self):
        res = super()._onchange_uom()
        new_weight = self.product_tmpl_id._get_weight_from_uom(self.uom_id)
        if new_weight:
            self.weight = new_weight
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            new_weight = self.env["product.template"]._get_weight_from_uom_id(
                vals.get("uom_id", False)
            )
            if new_weight:
                vals["weight"] = new_weight
        return super().create(vals_list)

    def write(self, vals):
        new_weight = self.env["product.template"]._get_weight_from_uom_id(
            vals.get("uom_id", False)
        )
        if new_weight:
            vals["weight"] = new_weight
        return super().write(vals)
