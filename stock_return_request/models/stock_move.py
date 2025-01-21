# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qty_returnable = fields.Float(
        digits="Product Unit of Measure",
        string="Returnable Quantity",
        compute="_compute_qty_returnable",
        readonly=True,
    )

    def _compute_qty_returnable(self):
        """Looks for chained returned moves to compute how much quantity
        from the original can be returned"""
        self.update({"qty_returnable": 0.0})
        for move in self:
            if not move.returned_move_ids:
                if move.state == "done":
                    move.qty_returnable = move.quantity_done
                else:
                    # TODO: Review if this option has sense
                    move.qty_returnable = move.reserved_availability
                continue
            move.qty_returnable = move.quantity_done - sum(
                move.returned_move_ids.mapped("qty_returnable")
            )

    def _get_lot_returnable_qty(self, lot_id, qty=0):
        """Looks for chained returned moves to compute how much quantity
        from the original can be returned for a given lot"""
        for move in self.filtered(lambda x: x.state not in ["draft", "cancel"]):
            mls = move.move_line_ids.filtered(lambda x: x.lot_id == lot_id)
            if move.state == "done":
                qty += sum(mls.mapped("qty_done"))
            else:
                qty += sum(mls.mapped("product_uom_qty"))
            qty -= move.returned_move_ids._get_lot_returnable_qty(lot_id)
        return qty

    def _action_assign(self):
        if self.env.context.get("skip_assign_move", False):
            # Avoid assign stock moves allowing create stock move lines manually
            return
        return super(StockMove, self)._action_assign()
