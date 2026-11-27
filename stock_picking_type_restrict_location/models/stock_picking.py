# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    location_id = fields.Many2one(
        domain="allowed_location_ids "
        "and [('id', 'child_of', allowed_location_ids)] or []"
    )
    location_dest_id = fields.Many2one(
        domain="allowed_location_dest_ids "
        "and [('id', 'child_of', allowed_location_dest_ids)] or []"
    )
    allowed_location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Allowed Source Locations",
        compute="_compute_allowed_location_ids",
        context={"active_test": False},
        help="The source location must be one of these locations or one of "
        "their sublocations. Empty when the source is not restricted.",
    )
    allowed_location_dest_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Allowed Destination Locations",
        compute="_compute_allowed_location_ids",
        context={"active_test": False},
        help="The destination location must be one of these locations or one "
        "of their sublocations. Empty when the destination is not restricted.",
    )

    @api.depends(
        "picking_type_id.restrict_location",
        "picking_type_id.default_location_src_id.usage",
        "picking_type_id.default_location_dest_id.usage",
        "return_id.location_id",
        "return_id.location_dest_id",
    )
    def _compute_allowed_location_ids(self):
        for picking in self:
            sources, destinations = picking.picking_type_id._get_restrict_locations()
            if sources:
                sources |= picking.return_id.location_dest_id
            if destinations:
                destinations |= picking.return_id.location_id
            picking.allowed_location_ids = sources
            picking.allowed_location_dest_ids = destinations

    @api.constrains("picking_type_id", "location_id", "location_dest_id")
    def _check_restrict_location(self):
        for picking in self.filtered(
            lambda picking: picking.state not in ("done", "cancel")
        ):
            if not picking._has_allowed_source():
                raise ValidationError(
                    self.env._(
                        "%(picking)s cannot take stock from %(location)s: the "
                        "operation type %(picking_type)s only allows "
                        "%(allowed_locations)s and their sublocations as "
                        "source.",
                        picking=picking.display_name,
                        location=picking.location_id.display_name,
                        picking_type=picking.picking_type_id.display_name,
                        allowed_locations=", ".join(
                            picking.allowed_location_ids.mapped("display_name")
                        ),
                    )
                )
            if not picking._has_allowed_destination():
                raise ValidationError(
                    self.env._(
                        "%(picking)s cannot send stock to %(location)s: the "
                        "operation type %(picking_type)s only allows "
                        "%(allowed_locations)s and their sublocations as "
                        "destination.",
                        picking=picking.display_name,
                        location=picking.location_dest_id.display_name,
                        picking_type=picking.picking_type_id.display_name,
                        allowed_locations=", ".join(
                            picking.allowed_location_dest_ids.mapped("display_name")
                        ),
                    )
                )

    def _has_allowed_source(self):
        self.ensure_one()
        allowed_locations = self.allowed_location_ids
        return not allowed_locations or self.location_id._is_inside_any(
            allowed_locations
        )

    def _has_allowed_destination(self):
        self.ensure_one()
        allowed_locations = self.allowed_location_dest_ids
        return not allowed_locations or self.location_dest_id._is_inside_any(
            allowed_locations
        )
