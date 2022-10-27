# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _update_assigned_state_to_inprogress(env):
    query = """
        UPDATE stock_picking_batch
        SET state = 'in_progress'
        WHERE state='assigned'
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _update_assigned_state_to_inprogress(env)
