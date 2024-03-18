# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, values):
        if not "route_ids" in values:
            return super().write(values)
        # As _compute_is_mto cannot use api.depends (or it would reset MTO
        # route on variants as soon as there is a change on the template routes),
        # we need to check which template in self had MTO route activated
        # or deactivated to force the recomputation of is_mto on variants
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        template_not_mto_before = self.filtered(lambda t: mto_route not in t.route_ids)
        res = super().write(values)
        templates_mto_after = self.filtered(lambda t: mto_route in t.route_ids)
        templates_mto_added = template_not_mto_before & templates_mto_after
        templates_mto_removed = (self - template_not_mto_before) & (self - templates_mto_after)
        (templates_mto_added | templates_mto_removed).product_variant_ids._compute_is_mto()
        return res

    @api.onchange("route_ids")
    def onchange_route_ids(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if mto_route not in self._origin.route_ids and mto_route in self.route_ids._origin:
            # Return warning activating MTO route
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("Activating MTO route will reset `Variant is MTO` setting on the variants.")
                }
            }
        if mto_route in self._origin.route_ids and mto_route not in self.route_ids._origin:
            # Return warning deactivating MTO route
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("Deactivating MTO route will reset `Variant is MTO` setting on the variants.")
                }
            }
