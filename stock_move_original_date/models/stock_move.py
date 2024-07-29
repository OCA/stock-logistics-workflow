# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    original_date = fields.Datetime(
        string="Original Date Scheduled",
        readonly=True,
        copy=False,
        help="Original Scheduled date on the confirmation of the stock move.",
    )

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super()._action_confirm(merge=merge, merge_into=merge_into)
        for move in moves:
            move.original_date = move.date
        return moves
