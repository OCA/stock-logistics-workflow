# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    put_in_pack_restriction = fields.Selection(
        selection=lambda self: self._selection_put_in_pack_restriction(),
        help="""
            Control restriction on the put in pack process.

            Options:
              * False (not set): No restriction.
              * Without Package: No destination package can be used.
              * With Package   : A destination package must be used.
        """,
    )

    @api.model
    def _selection_put_in_pack_restriction(self):
        return [
            ("no_package", "Destination Package Not Allowed"),
            ("with_package", "Destination Package required"),
        ]

    def _check_put_in_pack_allowed(self):
        """Raise an error if one of the picking types forbids packages."""
        forbidden = self.filtered(
            lambda picking_type: picking_type.put_in_pack_restriction == "no_package"
        )
        if forbidden:
            raise ValidationError(
                self.env._(
                    "Destination package can not be used with "
                    "%(picking_type_name)s transfer.",
                    picking_type_name=", ".join(forbidden.mapped("name")),
                )
            )
