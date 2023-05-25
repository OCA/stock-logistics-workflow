# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

SINGLEPACKAGE = "singlepackage"
MULTIPACKAGE = "multiplepackage"
NORESTRICTION = "norestriction"


class StockLocation(models.Model):
    _inherit = "stock.location"

    package_restriction = fields.Selection(
        selection=lambda self: self._selection_package_restriction(),
        help="Restriction on wich Packagings can be put on this location",
        required=True,
        store=True,
        default="norestriction",
    )

    @api.model
    def _selection_package_restriction(self):
        return [
            (
                SINGLEPACKAGE,
                "You cannot have products not part of a package on the location & "
                "you cannot have more than 1 package on the location",
            ),
            (
                MULTIPACKAGE,
                "You cannot have products not part of a package on the location",
            ),
            (NORESTRICTION, "No Restriction"),
        ]
