# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "stock_move_line", "lot_expiration_date"):
        env.cr.execute(
            """
            UPDATE stock_move_line
            SET expiration_date = lot_expiration_date
            WHERE expiration_date <> lot_expiration_date
                AND lot_expiration_date IS NOT NULL
                AND expiration_date IS NULL;
        """
        )
