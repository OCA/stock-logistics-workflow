# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields

IS_MTO_HELP = """
    Check or Uncheck this field to enable the Make To Order on the variant,
    independantly from its template configuration.
"""

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_mto = fields.Boolean(
        string="Variant is MTO",
        compute="_compute_is_mto",
        inverse="_inverse_is_mto",
        store=True,
        help=IS_MTO_HELP,
    )

    @api.depends("product_tmpl_id.route_ids")
    def _compute_is_mto(self):
        # We only want to force all variants `is_mto` to True when
        # the mto route is explicitely set on its template.
        # Watching the mto route is not enough, since we might
        # have a template with the mto route, and disabled the mto route
        # for a few of its variants
        # If a user sets another route on the variant, we do not want the
        # mto disabled variants to be updated.
        # To ensure that, the created `has_mto_route_changed` boolean field
        # is set to True only when the MTO route is set on a template.
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        templates = self.product_tmpl_id
        # Only variants with a template with the MTO route and has_mto_route_changed
        # should be updated.
        mto_templates = templates.filtered(
            lambda t: mto_route in t.route_ids and t.has_mto_route_changed
        )
        mto_variants = self.filtered(lambda p: p.product_tmpl_id in mto_templates)
        mto_variants.is_mto = True
        # For the other variants, keep their current value.
        other_variants = self - mto_variants
        for variant in other_variants:
            variant.is_mto = variant.is_mto
        # Then set template's has_mto_route_changed to False, as it
        # has been handled above
        templates.has_mto_route_changed = False

    def _inverse_is_mto(self):
        # When all variants of a template are `is_mto == False`, drop the MTO route
        # from the template, otherwise do nothing
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        for template in self.product_tmpl_id:
            is_mto = False
            for variant in template.product_variant_ids:
                if variant.is_mto:
                    is_mto = True
                    break
            # If no variant is mto, then drop the route of the template.
            if not is_mto:
                template.route_ids = [(3, mto_route.id, 0)]
