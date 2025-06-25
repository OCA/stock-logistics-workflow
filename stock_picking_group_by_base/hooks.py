# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs


def uninstall_hook(env):
    """
    This method will remove created index
    """
    index_name = "stock_picking_groupby_key_index"
    env.cr.execute(
        "DROP INDEX IF EXISTS %(index_name)s", dict(index_name=AsIs(index_name))
    )
