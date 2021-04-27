# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(cr, pool):
    cr.execute(
        "update stock_move_line set manual_lot_id=lot_id"
    )
