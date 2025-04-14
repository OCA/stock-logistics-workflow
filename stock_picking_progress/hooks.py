# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists, create_column

logger = logging.getLogger(__name__)


def setup_move_progress(env):
    """Update the 'progress' column for not-started or already done moves."""
    table = "stock_move"
    column = "progress"
    cr = env.cr
    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    logger.info("creating %s on table %s", column, table)
    field_spec = [
        (
            "progress",
            "stock.move",
            "stock_move",
            "float",
            "float",
            "stock_picking_progress",
            100.0,
        )
    ]
    openupgrade.add_fields(env, field_spec)
    logger.info("filling up %s on %s", column, table)
    cr.execute("""UPDATE stock_move SET progress =0 WHERE state = 'cancel'""")
    cr.execute(
        """
        UPDATE stock_move SET progress =(quantity / product_uom_qty) * 100
        WHERE state not in ('done', 'cancel') AND  product_uom_qty > 0.0
        """
    )


def setup_picking_progress(env):
    table = "stock_picking"
    column = "progress"
    _type = "float"
    cr = env.cr
    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    logger.info("creating %s on table %s", column, table)
    create_column(cr, table, column, _type)
    fill_column_query = """
        UPDATE stock_picking p
        SET progress = subquery.avg_progress
        FROM (
            SELECT sm.picking_id, avg(sm.progress) as avg_progress
            FROM stock_move sm
            GROUP BY sm.picking_id
        ) as subquery
        WHERE p.id = subquery.picking_id;
    """
    logger.info("filling up %s on %s", column, table)
    cr.execute(fill_column_query)


def pre_init_hook(env):
    setup_move_progress(env)
    setup_picking_progress(env)
