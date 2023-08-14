# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    force_date = fields.Datetime(
        compute="_compute_force_date",
        store=True,
        readonly=False,
        copy=False,
        help="Force the moves to a given date.",
    )

    @api.depends("picking_id.force_date")
    def _compute_force_date(self):
        for move in self:
            if move.picking_id:
                move.force_date = move.picking_id.force_date

    def _action_done(self, cancel_backorder=False):
        moves_todo = super()._action_done(cancel_backorder)
        for move in moves_todo:
            if move.force_date:
                move.write({"date": move.force_date})
                move.move_line_ids.write({"date": move.force_date})
        return moves_todo
