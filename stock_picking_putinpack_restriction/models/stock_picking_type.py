# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
        store=True,
    )

    @api.model
    def _selection_put_in_pack_restriction(self):
        return [
            ("no_package", "Destination Package Not Allowed"),
            ("with_package", "Destination Package required"),
        ]
