# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    allow_stock_picking_move_done_manual = fields.Boolean(
        related='picking_id.allow_stock_picking_move_done_manual')

    def _action_done_get_picking(self, moves, moves_todo):
        picking = super(StockMove, self)._action_done_get_picking(
            moves, moves_todo)
        for move in moves.filtered(lambda m: m.state != 'cancel'):
            picking = move.picking_id
        return picking

    @api.multi
    def action_manual_done_from_picking(self):
        for rec in self:
            rec.with_context(skip_backorder=True)._action_done()
            if rec.picking_id.state not in ["done", "cancel"]:
                rec.picking_id.action_assign()

    def _do_unreserve(self):
        non_done_self = self.filtered(lambda m: m.state != 'done')
        res = super(StockMove, non_done_self)._do_unreserve()
        return res
