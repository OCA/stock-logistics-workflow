# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _split(self, qty, restrict_partner_id=False):
        force_qty_to_backorder = self.env.context.get("force_moves_qty_to_backorder")
        if not force_qty_to_backorder:
            return super()._split(qty, restrict_partner_id=restrict_partner_id)
        if self.id not in force_qty_to_backorder:
            return []
        return super()._split(
            force_qty_to_backorder[self.id], restrict_partner_id=restrict_partner_id
        )
