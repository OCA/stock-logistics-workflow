# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

PARTNER_LOCATION_USAGES = ("supplier", "customer")


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_location = fields.Boolean(
        help="Transfers of this operation type can only take stock from its "
        "default source location or one of its sublocations, and send it to "
        "its default destination location or one of its sublocations. A "
        "vendor or customer location is not restricted.",
    )

    @api.constrains(
        "restrict_location", "default_location_src_id", "default_location_dest_id"
    )
    def _check_restrict_location(self):
        if self.env.context.get("restrict_location_defer_check"):
            return
        restricted_types = self.filtered("restrict_location")
        pickings = restricted_types._get_pickings_outside_restrict_locations()
        if pickings:
            names = pickings[:10].mapped("name")
            if len(pickings) > 10:
                names.append("...")
            raise ValidationError(
                self.env._(
                    "These transfers in progress use locations that "
                    "%(picking_types)s would not allow: %(pickings)s. Finish "
                    "them, cancel them or correct their locations first.",
                    picking_types=", ".join(
                        pickings.picking_type_id.mapped("display_name")
                    ),
                    pickings=", ".join(names),
                )
            )
        self.env["stock.rule"].search(
            [("picking_type_id", "in", restricted_types.ids)]
        )._check_restrict_location()

    def _get_restrict_locations(self):
        Location = self.env["stock.location"]
        if not self.restrict_location:
            return Location, Location
        return (
            self.default_location_src_id.filtered(
                lambda location: location.usage not in PARTNER_LOCATION_USAGES
            ),
            self.default_location_dest_id.filtered(
                lambda location: location.usage not in PARTNER_LOCATION_USAGES
            ),
        )

    def _get_pickings_outside_restrict_locations(self):
        Picking = self.env["stock.picking"]
        domains = []
        for picking_type in self:
            sources, destinations = picking_type._get_restrict_locations()
            location_domains = []
            if sources:
                location_domains.append(["!", ("location_id", "child_of", sources.ids)])
            if destinations:
                location_domains.append(
                    ["!", ("location_dest_id", "child_of", destinations.ids)]
                )
            if location_domains:
                domains.append(
                    expression.AND(
                        [
                            [("picking_type_id", "=", picking_type.id)],
                            expression.OR(location_domains),
                        ]
                    )
                )
        if not domains:
            return Picking
        return Picking.search(
            expression.AND(
                [
                    [("state", "not in", ("done", "cancel"))],
                    expression.OR(domains),
                ]
            )
        ).filtered(
            lambda picking: not picking._has_allowed_source()
            or not picking._has_allowed_destination()
        )
