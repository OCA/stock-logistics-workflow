# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picked = fields.Boolean(
        # Override std field
        inverse="_inverse_picked",
        copy=False,
    )
    qty_picked = fields.Float(inverse="_inverse_qty_picked", copy=False)

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
        total_demand = self.move_id.product_uom_qty
        total_reserved = sum(self.move_id.move_line_ids.mapped("quantity"))
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        if (
            float_compare(qty, self.quantity, precision_digits=prec) > 0
            and float_compare(total_reserved + qty, total_demand, precision_digits=prec)
            <= 0
        ):
            values["quantity"] = qty
        self.with_context(move_line_pick_qty=True).update(values)
        return True

    def _action_done(self):
        for ml in self:
            if ml.qty_picked and ml.picked and ml.qty_picked != ml.quantity:
                ml.quantity = ml.qty_picked
        return super()._action_done()
