# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_90

@openupgrade.migrate()
def migrate(env, version):
    # Link stock moves with invoice lines according old link
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET invoice_line_id = rel.account_invoice_line_id
        FROM account_invoice_line_stock_move_rel rel
        WHERE sm.id = rel.stock_move_id
            AND sm.invoice_line_id IS NULL
        """
    )
