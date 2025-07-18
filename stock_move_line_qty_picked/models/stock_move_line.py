# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    qty_picked = fields.Float()

    def _pick_qty(self, qty):
        self.ensure_one()
        values = {
            "qty_picked": qty,
            "picked": True,
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
        self.write(values)
        return True

    def _action_done(self):
        for ml in self:
            if ml.qty_picked and ml.picked and ml.qty_picked != ml.quantity:
                ml.quantity = ml.qty_picked
        return super()._action_done()
