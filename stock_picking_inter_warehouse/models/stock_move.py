from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _search_picking_for_assignation(self):
        # We do not want to merge pickings made in a transfer
        # between warehouses
        res = super()._search_picking_for_assignation()
        if res and any(
            self.move_orig_ids.mapped("picking_type_id").mapped(
                "disable_merge_picking_moves"
            )
        ):
            return False
        return res
