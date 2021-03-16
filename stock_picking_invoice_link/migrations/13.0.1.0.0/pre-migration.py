# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936

table_renames = [("stock_move_invoice_line_rel", None)]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.remove_tables_fks(env.cr, ["stock_move_invoice_line_rel"])
    openupgrade.rename_tables(env.cr, table_renames)
