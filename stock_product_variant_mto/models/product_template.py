# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_mto_route_changed = fields.Boolean()

    def write(self, values):
        if not "route_ids" in values:
            return super().write(values)
        # This route_ids change will trigger variant's _compute_is_mto.
        # We want to set variant's is_mto to True only if their
        # template has been set to True here ↓
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        template_not_mto_before = self.filtered(lambda t: mto_route not in t.route_ids)
        res = super().write(values)
        template_mto_after = self.filtered(lambda t: mto_route in t.route_ids)
        # Templates where mto route has changed are those where
        # the mto route has been set
        templates_mto_set = template_not_mto_before & template_mto_after
        templates_mto_set.has_mto_route_changed = True
