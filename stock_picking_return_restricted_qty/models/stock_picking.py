# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _cap_return_restricted_qty(self):
        """Lower each restricted return move to what can still be returned."""
        for return_move in self.move_ids.filtered(
            lambda m: (
                m.state not in ("done", "cancel")
                and m.origin_returned_move_id
                and m._is_return_qty_restricted()
            )
        ):
            orig_move = return_move.origin_returned_move_id
            returnable = orig_move.product_id.uom_id._compute_quantity(
                orig_move._get_returned_restricted_quantity(excluded_moves=return_move),
                return_move.uom_id,
                rounding_method="DOWN",
            )
            if return_move.uom_id.compare(return_move.product_uom_qty, returnable) > 0:
                return_move.product_uom_qty = returnable

    def _create_return(self):
        # The core fills the whole quantity when returning a return
        new_picking = super(
            StockPicking, self.with_context(skip_return_restricted_qty_check=True)
        )._create_return()
        new_picking.with_context(
            skip_return_restricted_qty_check=False
        )._cap_return_restricted_qty()
        return new_picking.with_env(self.env)

    def action_return_all(self):
        res = super(
            StockPicking, self.with_context(skip_return_restricted_qty_check=True)
        ).action_return_all()
        self._cap_return_restricted_qty()
        return res
