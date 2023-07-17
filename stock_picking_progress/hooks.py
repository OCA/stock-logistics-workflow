# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists, create_column

logger = logging.getLogger(__name__)


def setup_move_line_progress(cr):
    """Update the 'progress' column for move lines."""
    table = "stock_move_line"
    column = "progress"
    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    logger.info("creating %s on table %s", column, table)
    field_spec = [
        (
            "progress",
            "stock.move.line",
            "stock_move_line",
            "float",
            "float",
            "stock_picking_progress",
            100.0,
        )
    ]
    openupgrade.add_fields(env, field_spec)
    logger.info("filling up %s on %s", column, table)
    cr.execute("""UPDATE stock_move_line SET progress =0 WHERE state = 'cancel'""")
    cr.execute(
        """
        UPDATE stock_move_line SET progress =(qty_done / reserved_qty) * 100
        WHERE state not in ('done', 'cancel') AND  reserved_qty > 0.0
        """
    )


def setup_move_progress(cr):
    """Update the 'progress' column for not-started or already done moves."""
    table = "stock_move"
    column = "progress"
    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
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
        UPDATE stock_move SET progress =(quantity_done / product_uom_qty) * 100
        WHERE state not in ('done', 'cancel') AND  product_uom_qty > 0.0
        """
    )


def setup_picking_progress(cr):
    table = "stock_picking"
    column = "progress"
    _type = "float"
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


def pre_init_hook(cr):
    setup_move_line_progress(cr)
    setup_move_progress(cr)
    setup_picking_progress(cr)
