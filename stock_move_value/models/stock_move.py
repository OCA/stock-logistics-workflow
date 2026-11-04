# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    value_currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id"
    )
    move_value = fields.Monetary(
        compute="_compute_move_value",
        store=True,
        currency_field="value_currency_id",
        help="Value of the move including related SVL values (i.e. price differences "
        "and landed costs)",
    )
    move_origin_value = fields.Monetary(
        currency_field="value_currency_id",
        help="Corresponding value of the origin move as of the the time move was done. "
        "Only updated for vendor returns.",
    )
    value_discrepancy = fields.Monetary(
        currency_field="value_currency_id",
        help="Move Value + Move Origin Value. Only updated for vendor returns.",
    )
    to_review_discrepancy = fields.Boolean(
        help="Selected when Value Discrepancy is not zero. Users are expected to "
        "unselect it when review is done.",
    )

    @api.depends(
        "stock_valuation_layer_ids",
        "stock_valuation_layer_ids.stock_valuation_layer_ids",
    )
    def _compute_move_value(self):
        for move in self:
            # There can be multiple svls per move in case landed costs are entered
            move.move_value = sum(move.sudo().stock_valuation_layer_ids.mapped("value"))

    def _action_done(self, cancel_backorder=False):
        origin_values = defaultdict(dict)
        for move in self:
            if not move._is_out():
                continue
            origin_move = move.origin_returned_move_id
            if not origin_move:
                continue
            # There should be only one record
            origin_svls = origin_move.stock_valuation_layer_ids.filtered(
                lambda r: r.quantity > 0
            )
            origin_values[move.id] = {
                "quantity": origin_svls.quantity,
                "value": origin_svls.value,
            }
        moves = super()._action_done(cancel_backorder)
        for move in moves:
            move.move_value = sum(move.sudo().stock_valuation_layer_ids.mapped("value"))
            if not move._is_out() or not move.origin_returned_move_id:
                continue
            move.move_origin_value = (
                origin_values[move.id]["value"]
                * move.product_qty
                / origin_values[move.id]["quantity"]
            )
            move.value_discrepancy = move.move_origin_value + move.move_value
            if move.value_discrepancy != 0.0:
                move.to_review_discrepancy = True
        return moves
