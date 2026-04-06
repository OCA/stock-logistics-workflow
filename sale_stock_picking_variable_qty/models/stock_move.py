# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_final_sale_line_id(self):
        # Consider only pick/pack moves
        return (self.browse(self._rollup_move_dests())).sale_line_id

    def _action_done(self, cancel_backorder=False):
        self._adjust_variable_quantity(cancel_backorder=cancel_backorder)
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _adjust_variable_quantity(self, cancel_backorder=False):
        """For moves where qty_done ≠ qty_demanded spread that new quantity across every
        move_dest_id.
        """
        # It doesn't make sense to analyize 0 qty moves as they're clearly not done
        for move in self.filtered(
            lambda move: move.quantity
            and move.picking_type_id.sale_stock_picking_variable_qty
        ):
            # There's a backorder to complete the remaining qty
            if move.quantity < move.product_uom_qty and not cancel_backorder:
                continue
            # Nothing to do if the demand fits the qty done, let's avoid changes
            rounding = move.product_uom.rounding
            if (
                float_compare(
                    move.quantity,
                    move.product_uom_qty,
                    precision_rounding=rounding,
                )
                == 0
            ):
                continue
            sale_line = move._get_final_sale_line_id()
            if not sale_line:
                continue
            if sale_line.product_id.invoice_policy == "order":
                continue
            # The quantity of the move might be a partial of the sale line demand
            locked_sale_line_qty = sale_line.product_uom_qty - move.product_uom_qty
            # Finally we adjust just the variable demand corresponding to this move
            sale_line.product_uom_qty = locked_sale_line_qty + move.quantity
