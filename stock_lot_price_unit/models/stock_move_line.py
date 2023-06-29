# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _skip_lot_price_unit_update(self):
        """Return whether to skip updating the price unit of the lot."""
        self.ensure_one()
        lot = self.lot_id
        # If lot.price_unit has already been updated, respect the existing value.
        if not lot or lot.price_unit != 0.0:
            return True
        return False
