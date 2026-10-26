# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        # The backorder wizard already warns about moves left short when the
        # backorder is cancelled.
        logged_moves = self.env["stock.move"]
        if self.env.context.get("picking_ids_not_to_backorder"):
            logged_moves = self.browse(
                self.env.context["picking_ids_not_to_backorder"]
            ).move_ids.filtered(
                lambda move: float_compare(
                    move.product_uom_qty,
                    move._get_picked_quantity(),
                    precision_rounding=move.product_uom.rounding,
                )
                > 0
            )
        result = super()._action_done()
        shortages = (self.move_ids - logged_moves)._get_variable_quantity_shortages()
        for picking in self.env["stock.move"].concat(*shortages).picking_id:
            picking._log_less_quantities_than_expected(
                {
                    move: quantities
                    for move, quantities in shortages.items()
                    if move.picking_id == picking
                }
            )
        return result
