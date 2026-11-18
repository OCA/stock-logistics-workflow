# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_returned_restricted_quantity(self, excluded_moves=None):
        """Quantity of this move, in the product UoM, that is still on the
        hands of the one who tries to return it."""
        self.ensure_one()
        qty = self.product_qty
        # In 20.0 a return of a return is not linked as destination move
        dest_moves = (self.move_dest_ids | self.returned_move_ids) - (
            excluded_moves or self.browse()
        )
        for line in dest_moves.move_line_ids:
            if (
                line.move_id.origin_returned_move_id
                and line.move_id.origin_returned_move_id != self
            ):
                continue
            if line.state in {"partially_available", "assigned", "done"}:
                qty -= line.quantity_product_uom
        return max(qty, 0.0)

    def _is_return_qty_restricted(self):
        self.ensure_one()
        return bool(
            self.origin_returned_move_id.picking_id.picking_type_id.restrict_return_qty
        )

    def _check_return_restricted_qty(self, get_quantity):
        if self.env.context.get("skip_return_restricted_qty_check"):
            return
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        for move in self:
            if move.state == "cancel" or not move._is_return_qty_restricted():
                continue
            returnable = move.origin_returned_move_id._get_returned_restricted_quantity(
                excluded_moves=move
            )
            if (
                float_compare(
                    get_quantity(move), returnable, precision_digits=precision
                )
                > 0
            ):
                raise UserError(
                    self.env._("Return more quantities than delivered is not allowed.")
                )

    @api.constrains("product_uom_qty", "uom_id")
    def _check_return_restricted_demand(self):
        self._check_return_restricted_qty(lambda move: move.product_qty)

    def _action_done(self, cancel_backorder=False):
        # Only picked lines are kept by the core when the move is picked
        self.filtered(
            lambda m: m.state not in ("done", "cancel") and m.picked
        )._check_return_restricted_qty(
            lambda move: sum(
                move.move_line_ids.filtered("picked").mapped("quantity_product_uom")
            )
        )
        return super()._action_done(cancel_backorder=cancel_backorder)
