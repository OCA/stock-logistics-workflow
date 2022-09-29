# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def name_get(self):
        """Move lots without a qty on hand at the end of the list"""
        res = super().name_get()
        if self.env.context.get("name_search_qty_on_hand_first"):
            no_qty_lot_ids = self.search([("product_qty", "=", 0)]).ids
            res_copy = res.copy()
            to_reorder = []
            for pos, lot_id_name in enumerate(res):
                if lot_id_name[0] in no_qty_lot_ids:
                    to_reorder.append(res_copy.pop(pos - len(to_reorder)))
            res_copy += to_reorder
            res = res_copy
        return res
