# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade

_table_renames = [("stock_move_invoice_line_rel", "old_stock_move_invoice_line_rel")]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renames)
    # Remove FKs on old relations for avoiding further problems
    openupgrade.lift_constraints(env.cr, _table_renames[0][1], "move_id")
    openupgrade.lift_constraints(
        env.cr, "account_invoice_stock_picking_rel", "picking_id"
    )
    # Add temporary table for avoiding the automatic launch of the compute method
    openupgrade.logged_query(
        env.cr, "CREATE TABLE account_move_stock_picking_rel (temp INTEGER)",
    )
