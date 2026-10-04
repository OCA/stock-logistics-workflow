# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _get_putaway_recompute_domain(self):
        """
        Returns the domain to filter all stock move lines that require
        a putaway recomputation.
        """
        domain = [
            ("state", "not in", ("done", "cancel")),
            ("can_recompute_putaways", "=", True),
            ("qty_done", "=", 0),
            ("picking_id", "!=", False),
        ]
        return domain

    @api.model
    def cron_auto_recompute_putaways(self):
        """
        Finds all stock move lines that are candidates for putaway recomputation
        and trigger putaway recomputation on them.
        """

        lines_to_recompute = self.search(self._get_putaway_recompute_domain())

        if lines_to_recompute:
            lines_to_recompute.action_recompute_putaways()

        return True
