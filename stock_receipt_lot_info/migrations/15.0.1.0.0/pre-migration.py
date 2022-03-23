# Copyright 2022 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936

_field_renames = [
    ("stock.move.line", "stock_move_line", "lot_life_date", "lot_expiration_date"),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    for field in _field_renames:
        if openupgrade.table_exists(cr, field[1]) and openupgrade.column_exists(
            cr, field[1], field[2]
        ):
            openupgrade.rename_fields(env, [field])
