# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import Domain


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _is_auto_batchable(self, picking=None):
        # Early exit if partner is not allowed for batch grouping
        if self.partner_id and not self.partner_id.allow_batch_grouping:
            return False
        return super()._is_auto_batchable(picking=picking)

    def _get_possible_pickings_domain(self):
        # Exclude pickings with partners not allowed for batch grouping
        domain = super()._get_possible_pickings_domain()
        domain &= Domain(
            [
                "|",
                ("partner_id", "=", False),
                ("partner_id.allow_batch_grouping", "=", True),
            ]
        )
        return domain
