# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        self._adjust_variable_quantity()
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _adjust_variable_quantity(self):
        """For moves where qty_done ≠ qty_demanded spread that new quantity across every
        move_dest_id.
        """
        # TODO:
        #   * Make this optionable (by operation or whatever)
        #   * Handle correctly all the dest moves cases to spread or not the quantity
        for move in self.filtered("move_dest_ids"):
            rounding = move.product_uom.rounding
            if (
                float_compare(
                    move.quantity_done,
                    move.product_uom_qty,
                    precision_rounding=rounding,
                )
                == 0
            ):
                continue
            qty_left = move.quantity_done
            # Spread across dest moves
            # FIXME: this won't be correct when the origin operations are split across
            # lots, packages, etc...
            for move_dest in move.move_dest_ids:
                # Nothing left -> don't change anything
                if float_compare(qty_left, 0.0, precision_rounding=rounding) <= 0:
                    continue
                assignable = min(move_dest.product_uom_qty, qty_left)
                move_dest.product_uom_qty = assignable
                qty_left -= assignable
            # Assign the remaining to the first destination move
            if float_compare(qty_left, 0.0, precision_rounding=rounding) > 0:
                move.move_dest_ids[:1].product_uom_qty += qty_left
