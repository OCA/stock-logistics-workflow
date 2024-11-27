# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    putaway_default_to_last_location = fields.Boolean(
        help="If checked, the product will be putaway in the last location "
        "used by default.",
    )

    def _get_last_putaway_location(self, product):
        return (
            self.env["stock.move.line"]
            .search(
                [
                    ("product_id", "=", product.id),
                    ("location_dest_id", "child_of", self.id),
                    ("state", "=", "done"),
                ],
                order="date desc",
                limit=1,
            )
            .location_dest_id
        )

    def _get_putaway_strategy(self, product):
        putaway_location = super()._get_putaway_strategy(product)
        if not putaway_location and self.putaway_default_to_last_location:
            putaway_location = self._get_last_putaway_location(product)
        return putaway_location
