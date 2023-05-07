# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Pre-create column for avoiding triggering the compute method
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS reservation_date DATE"
    )
    openupgrade.logged_query(
        env.cr, "UPDATE stock_move sm SET sm.reservation_date = sm.date_expected"
    )
