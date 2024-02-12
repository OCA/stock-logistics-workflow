# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange('uom_id')
    def _onchange_uom_id(self):
        res = super()._onchange_uom_id()
        new_weight = self._get_weight_from_uom(self.uom_id)
        if new_weight:
            self.weight = new_weight
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            new_weight = self._get_weight_from_uom_id(vals.get("uom_id", False))
            if new_weight:
                vals["weight"] = new_weight
        return super().create(vals_list)

    def write(self, vals):
        new_weight = self._get_weight_from_uom_id(vals.get("uom_id", False))
        if new_weight:
            vals["weight"] = new_weight
        return super().write(vals)

    @api.model
    def _get_weight_from_uom_id(self, uom_id):
        if not uom_id:
            return
        return self._get_weight_from_uom(self.env["uom.uom"].browse(uom_id))

    @api.model
    def _get_weight_from_uom(self, uom):
        if not uom.measure_type == "weight":
            return
        return uom._compute_quantity(
            1,
            self._get_weight_uom_id_from_ir_config_parameter()
        )
