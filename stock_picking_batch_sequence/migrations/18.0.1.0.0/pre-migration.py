#  Copyright 2026 Tecnativa - Carlos Roca
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # "batch_sequence" on stock.picking is also provided by core's own
    # stock_picking_batch module (same name, same purpose: ordering pickings
    # within a batch) -- by the time this script runs, stock_picking_batch's
    # own auto_init has already created the column, so renaming into it
    # raises psycopg2.errors.DuplicateColumn. Copy the data across instead.
    if openupgrade.column_exists(env.cr, "stock_picking", "sequence"):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_picking
            SET batch_sequence = sequence
            WHERE sequence IS NOT NULL
            """,
        )
    openupgrade.rename_fields(
        env,
        [
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
