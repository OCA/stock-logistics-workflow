from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        # We explicitly set `move_type` here because during the picking creation,
        # if 'move_type' is not present in `vals` and a `group_id` is provided,
        # the compute method is not triggered. This is due to the logic in
        # stock.picking's `create()` method.
        # Therefore, to ensure the correct `move_type` is set based on the picking type,
        # we must explicitly assign it here.
        picking_type = self.mapped("picking_type_id")
        if picking_type.force_move_type:
            res["move_type"] = picking_type.move_type
        return res
