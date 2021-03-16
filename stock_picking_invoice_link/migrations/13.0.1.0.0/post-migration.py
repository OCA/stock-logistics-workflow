# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936
from psycopg2.extensions import AsIs


@openupgrade.migrate()
def migrate(env, version):
    old_table = AsIs(openupgrade.get_legacy_name("stock_move_invoice_line_rel"))
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_move_invoice_line_rel
        (invoice_line_id, move_id)
        SELECT aml.id, rel.move_id
        FROM %s rel
        JOIN account_move_line aml ON aml.old_invoice_line_id = rel.invoice_line_id
        """,
        (old_table,),
    )
    openupgrade.remove_tables_fks(env.cr, ["account_invoice_stock_picking_rel"])
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move_stock_picking_rel
        (account_move_id, stock_picking_id)
        SELECT am.id, rel.stock_picking_id
        FROM account_invoice_stock_picking_rel rel
        JOIN account_move am ON am.old_invoice_id = rel.account_invoice_id
        """,
    )
