# Copyright 2025 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picked = fields.Boolean(
        # Override std field
        inverse="_inverse_picked",
        copy=False,
    )
    qty_picked = fields.Float(
        inverse="_inverse_qty_picked", copy=False, digits="Product Unit"
    )

    def _inverse_picked(self):
        if self.env.context.get("move_line_pick_qty"):
            return
        for rec in self:
            # Reset picked qty to 0
            if not rec.picked:
                rec._pick_qty(0)
                continue
            # Pick full quantity when 'picked = True' and no qty were picked
            if not rec.qty_picked:
                if not rec.quantity:
                    # When making an inventory with a difference of 0, a move
                    # and move line are created with a quantity of 0. The move
                    # is flagged as picked which will flag the move line as
                    # picked. As the quantity is 0, do not reset picked to
                    # False otherwise it get's deleted on action_done.
                    continue
                rec._pick_qty(rec.quantity)

    def _inverse_qty_picked(self):
        if self.env.context.get("move_line_pick_qty"):
            return
        for rec in self:
            rec._pick_qty(rec.qty_picked)

    def _pick_qty(self, qty):
        self.ensure_one()
        values = {
            "qty_picked": qty,
            "picked": bool(qty),
        }
        move = self.move_id
        total_demand = move.product_uom_qty
        total_reserved = move.quantity
        qty_in_move_uom = self.product_uom_id._compute_quantity(
            qty, move.product_uom, round=False
        )
        if (
            self.product_uom_id.compare(qty, self.quantity) > 0
            and move.product_uom.compare(total_reserved + qty_in_move_uom, total_demand)
            <= 0
        ):
            values["quantity"] = qty
        self.with_context(move_line_pick_qty=True).update(values)
        return True
