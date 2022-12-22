# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists, create_column

logger = logging.getLogger(__name__)


def setup_move_line_progress(cr):
    """Update the 'progress' column for move lines."""
    table = "stock_move_line"
    column = "progress"
    _type = "float"
    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    logger.info("creating %s on table %s", column, table)
    create_column(cr, table, column, _type)
    fill_column_query = """
        UPDATE stock_move_line
        SET progress = CASE
            WHEN (state = 'done') THEN 100
            WHEN (product_uom_qty IS NULL or product_uom_qty = 0.0) THEN 0.0
            ELSE (qty_done / product_uom_qty) * 100
        END;
    """
    logger.info("filling up %s on %s", column, table)
    cr.execute(fill_column_query)


def setup_move_progress(cr):
    """Update the 'progress' column for not-started or already done moves."""
    table = "stock_move"
    column = "progress"
    _type = "float"

    if column_exists(cr, table, column):
        logger.info("%s already exists on %s, skipping setup", column, table)
        return
    logger.info("creating %s on table %s", column, table)
    create_column(cr, table, column, _type)
    fill_column_query = """
        UPDATE stock_move
        SET progress = CASE
            WHEN (state = 'done') THEN 100
            WHEN (state in ('draft', 'confirmed')) THEN 0.0
            WHEN (product_uom_qty IS NULL or product_uom_qty = 0.0) THEN 0.0
        END;
    """
    logger.info("filling up %s on %s", column, table)
    cr.execute(fill_column_query)


def setup_move_progress_post(env):
    """Update the 'progress' column for moves in progress.

    It needs to be processed in post as the computation
    depends on the computed `quantity_done` field.
    """
    moves = env["stock.move"].search(
        [("state", "in", ["waiting", "partially_available", "assigned"])]
    )
    moves._compute_progress()


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
            SELECT sml.picking_id, avg(sml.progress) as avg_progress
            FROM stock_move_line sml
            GROUP BY sml.picking_id
        ) as subquery
        WHERE p.id = subquery.picking_id;
    """
    logger.info("filling up %s on %s", column, table)
    cr.execute(fill_column_query)


def pre_init_hook(cr):
    setup_move_line_progress(cr)
    setup_move_progress(cr)
    setup_picking_progress(cr)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    setup_move_progress_post(env)
