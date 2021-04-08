# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.logging()
def insert_invoice_line_stock_move_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_move_invoice_line_rel
        (invoice_line_id, move_id)
        SELECT aml.id, rel.move_id
        FROM old_stock_move_invoice_line_rel rel
        JOIN account_move_line aml ON aml.old_invoice_line_id = rel.invoice_line_id""",
    )


def insert_invoice_picking_rel(env):
    # Remove temp table and re-create m2m table through ORM method
    openupgrade.logged_query(env.cr, "DROP TABLE account_move_stock_picking_rel")
    Move = env["account.move"]
    Move._fields["picking_ids"].update_db(Move, False)
    # Fill values from existing table
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move_stock_picking_rel
        (account_move_id, stock_picking_id)
        SELECT am.id, rel.stock_picking_id
        FROM account_invoice_stock_picking_rel rel
        JOIN account_move am ON am.old_invoice_id = rel.account_invoice_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    insert_invoice_line_stock_move_rel(env)
    insert_invoice_picking_rel(env)
