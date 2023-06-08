# Copyright 2023, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    original_qty = fields.Float(
        readonly=True,
    )

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super()._action_confirm(merge=merge, merge_into=merge_into)
        for move in moves:
            move.original_qty = move.product_uom_qty
        return moves
