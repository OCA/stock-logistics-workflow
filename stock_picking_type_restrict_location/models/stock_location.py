# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _is_inside_any(self, locations):
        self.ensure_one()
        return any(self._child_of(location) for location in locations)
