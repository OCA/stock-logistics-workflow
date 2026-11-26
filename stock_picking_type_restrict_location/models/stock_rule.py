# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.constrains(
        "active",
        "action",
        "auto",
        "picking_type_id",
        "location_src_id",
        "location_dest_id",
        "location_dest_from_rule",
    )
    def _check_restrict_location(self):
        if self.env.context.get("restrict_location_defer_check"):
            return
        for rule in self.filtered("active"):
            pulls = rule.action in ("pull", "pull_push")
            pushes = rule.action in ("push", "pull_push") and rule.auto != "transparent"
            feeds_production = (
                not pushes and rule.location_dest_id.usage == "production"
            )
            if feeds_production or (not pulls and not pushes):
                continue
            sources, destinations = rule.picking_type_id._get_restrict_locations()
            if (
                sources
                and rule.location_src_id
                and not rule.location_src_id._is_inside_any(sources)
            ):
                raise ValidationError(
                    self.env._(
                        "The rule %(rule)s takes stock from %(location)s, but "
                        "the operation type %(picking_type)s only allows "
                        "%(allowed_locations)s and their sublocations as "
                        "source.",
                        rule=rule.display_name,
                        location=rule.location_src_id.display_name,
                        picking_type=rule.picking_type_id.display_name,
                        allowed_locations=", ".join(sources.mapped("display_name")),
                    )
                )
            if (
                destinations
                and (pushes or rule.location_dest_from_rule)
                and not rule.location_dest_id._is_inside_any(destinations)
            ):
                raise ValidationError(
                    self.env._(
                        "The rule %(rule)s sends stock to %(location)s, but "
                        "the operation type %(picking_type)s only allows "
                        "%(allowed_locations)s and their sublocations as "
                        "destination.",
                        rule=rule.display_name,
                        location=rule.location_dest_id.display_name,
                        picking_type=rule.picking_type_id.display_name,
                        allowed_locations=", ".join(
                            destinations.mapped("display_name")
                        ),
                    )
                )
