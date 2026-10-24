# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        # OVERRIDE to add important information in the help message.
        # `batch_creation_type` is the field shown on the form on 20.0; it
        # copies `auto_batch`'s help at class definition, so both are updated.
        res = super().fields_get(allfields, attributes)
        note = "\n\n" + self.env._(
            "Note: Partners must be 'Allowed for batch grouping' for the "
            "picking to be included in batches."
        )
        for fname in ("auto_batch", "batch_creation_type"):
            if fname in res and res[fname].get("help"):
                res[fname]["help"] += note
        return res
