# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """
        Auto-assign as done the quantity proposed for the lots.
        Keep this method to avoid extra write after picking _action_assign
        """
        self.ensure_one()
        res = super()._prepare_move_line_vals(quantity, reserved_quant)
        if not self.picking_id.auto_fill_operation:
            return res
        elif self.picking_id.picking_type_id.avoid_lot_assignment and res.get("lot_id"):
            return res
        if self.quantity_done != self.product_uom_qty:
            # Not assign qty_done for extra moves in over processed quantities
            res.update({"qty_done": res.get("product_uom_qty", 0.0)})
        return res

    def _action_assign(self):
        """
        Update stock move line quantity done field with reserved quantity.
        This method take into account incoming and outgoing moves.
        We can not use _prepare_move_line_vals method because this method only
        is called for a new lines.
        """
        res = super()._action_assign()
        for line in self.filtered(
            lambda m: m.state
            in ["confirmed", "assigned", "waiting", "partially_available"]
        ):
            if (
                line._should_bypass_reservation()
                or not line.picking_id.auto_fill_operation
            ):
                return res
            lines_to_update = line.move_line_ids.filtered(
                lambda l: l.qty_done != l.product_uom_qty
            )
            for move_line in lines_to_update:
                if (
                    not line.picking_id.picking_type_id.avoid_lot_assignment
                    or not move_line.lot_id
                ):
                    move_line.qty_done = move_line.product_uom_qty
        return res
