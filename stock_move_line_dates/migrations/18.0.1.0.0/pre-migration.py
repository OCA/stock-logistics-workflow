# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "stock_move_line", "date_schedule"):
        openupgrade.rename_columns(
            env.cr,
            {
                "stock_move_line": [
                    ("date_schedule", "scheduled_date"),
                ],
            },
        )
