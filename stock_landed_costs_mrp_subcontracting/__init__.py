from . import models

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Before this module you receive partials from subcontracted vendor
    # Backorders got wrong related origin_move_ids from manufacturing orders
    # This script tries to correct associate
    # stock moves on purchase_orders on field move_orig_ids
    purchase_orders = env["purchase.order"].search([])
    move_model = env["stock.move"]
    for purchase_order in purchase_orders:
        moves = move_model.search(
            [
                ("is_subcontract", "=", True),
                ("purchase_line_id.order_id", "=", purchase_order.id),
                ("state", "!=", "cancel"),
            ],
            order="date",
        )
        remaining_moves = moves
        for move in moves.sorted(lambda x: len(x.move_orig_ids)):
            moves_with_one_origin_ids = remaining_moves.filtered(
                lambda x: len(x.move_orig_ids) == 1
            )
            for iteration_move in moves:
                if len(iteration_move.move_orig_ids) > 1:
                    for duplicated_moves in moves_with_one_origin_ids.mapped(
                        "move_orig_ids"
                    ):
                        if duplicated_moves.id in iteration_move.move_orig_ids.ids:
                            iteration_move.write(
                                {"move_orig_ids": [(3, duplicated_moves.id)]}
                            )
            remaining_moves -= move
