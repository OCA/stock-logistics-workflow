# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def fields_get(self, allfields=None, attributes=None):
        # OVERRIDE to add important information in the help message
        res = super().fields_get(allfields, attributes)
        if "auto_batch" in res:
            if res["auto_batch"].get("help"):
                res["auto_batch"]["help"] += "\n\n" + self.env._(
                    "Note: Partners must be 'Allowed for batch grouping' for the "
                    "picking to be included in batches."
                )
        return res
