# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade
from openupgradelib import openupgrade_tools


@openupgrade.migrate()
def migrate(env, version):
    # If exists the column and is False so the user wants automatic assignment
    if openupgrade_tools.column_exists(
            env.cr, 'stock_picking_type', 'avoid_internal_assignment'):
        openupgrade.logged_query(
            env.cr, """
            UPDATE stock_picking_type
            SET auto_fill_operation = True,
                avoid_lot_assignment = False
            WHERE NOT avoid_internal_assignment"""
        )
