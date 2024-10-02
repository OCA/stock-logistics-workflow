# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_moves_to_cancel_from_backorders(self, move):
        self.ensure_one()
        moves = self.env["stock.move"]
        if move.move_orig_ids:
            moves_done = move.move_orig_ids.filtered(lambda m: m.state == "done")
            done_previous_moves_qty = sum(m.product_qty for m in moves_done)
            if done_previous_moves_qty >= move.product_qty:
                moves = move.move_orig_ids.filtered(
                    lambda m: m.state not in ["done", "cancel"]
                )
        return moves

    def _action_done(self):
        if self.env.context.get("cancel_backorder", False):
            to_cancel_moves = self.env["stock.move"]
            for rec in self:
                if rec.company_id.stock_picking_backorder_link:
                    for move in rec.move_lines:
                        if move.move_orig_ids:
                            moves_done = move.move_orig_ids.filtered(
                                lambda m: m.state == "done"
                            )
                            done_previous_moves_qty = sum(
                                m.quantity_done for m in moves_done
                            )
                            if done_previous_moves_qty >= move.quantity_done:
                                to_cancel_moves |= move.move_orig_ids.filtered(
                                    lambda m: m.state not in ["done", "cancel"]
                                )
                        if move.move_dest_ids and move.product_qty > move.quantity_done:
                            move.propagate_move_dest_qty_reduction(
                                qty=move.product_qty - move.quantity_done
                            )
            to_cancel_moves._action_cancel()
        return super()._action_done()

    def action_cancel(self):
        if self.env.company.stock_picking_backorder_link:
            to_cancel_moves = self.env["stock.move"]
            # Just cancel previous moves for backorders,
            # if you cancel a normal picking does not do anything new.
            for rec in self.filtered(lambda p: p.backorder_id):
                for move in rec.move_lines:
                    if move.move_orig_ids:
                        to_cancel_moves |= move.move_orig_ids.filtered(
                            lambda m: m.state not in ["done", "cancel"]
                            and m.product_qty == move.product_qty
                        )
            to_cancel_moves._action_cancel()
        return super().action_cancel()
