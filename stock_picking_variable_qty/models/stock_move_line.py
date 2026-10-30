# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        done_moves = self.env["stock.move"]
        if "quantity" in vals or "product_uom_id" in vals:
            done_moves = self.filtered(lambda line: line.state == "done").move_id
        res = super().write(vals)
        done_moves._sync_variable_quantity_dest_moves()
        return res
