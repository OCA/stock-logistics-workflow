#  Copyright 2026 Tecnativa - Carlos Roca
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "stock.picking",
                "stock_picking",
                "sequence",
                "batch_sequence",
            ),
            (
                "stock.move",
                "stock_move",
                "picking_sequence",
                "picking_batch_sequence",
            ),
            (
                "stock.move.line",
                "stock_move_line",
                "picking_sequence",
                "picking_batch_sequence",
            ),
        ],
    )
