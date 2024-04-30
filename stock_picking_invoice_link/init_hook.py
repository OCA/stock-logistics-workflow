# Copyright 2023 ForgeFlow, S.L.
# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from collections import deque

from odoo import SUPERUSER_ID, api
from odoo.tools import sql

_logger = logging.getLogger(__name__)


def _create_picking_count(cr):
    """Extracted to reuse in migration script. TODO: It can be merged into a sole
    method in v16"""
    _logger.info("Creating column: picking_count for table account_move")
    cr.execute(
        """
    ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS picking_count INTEGER;
    """
    )


def _populate_picking_count(cr):
    """Extracted to reuse in migration script. TODO: It can be merged into a sole
    method in v16"""
    _logger.info("Populating values for column picking_count in table account_move")
    cr.execute(
        """
        UPDATE account_move am SET picking_count = t.picking_count
        FROM (
            SELECT
                am.id AS account_move_id,
                COUNT(DISTINCT sm.picking_id) AS picking_count
            FROM
                account_move am
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN stock_move_invoice_line_rel rel
                    ON rel.invoice_line_id = aml.id
                JOIN stock_move sm
                    ON sm.id = rel.move_id
            WHERE
                sm.picking_id IS NOT NULL
            GROUP BY
                am.id
        ) t
        WHERE am.id = t.account_move_id;
    """
    )


def pre_init_hook(cr):
    """Avoid pre-computations with the ORM"""
    _create_picking_count(cr)
    _populate_picking_count(cr)
    _logger.info(
        "Create temporary table to avoid the automatic launch of the compute method in "
        "the Many2one field account.move.picking_ids"
    )
    if not sql.table_exists(cr, "account_move_stock_picking_rel"):
        cr.execute(
            """CREATE TABLE account_move_stock_picking_rel
            (account_move_id integer,stock_picking_id integer)"""
        )


def post_init_hook(cr, registry):
    """Speed-up pre-computations"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Dropping temporary account_move_stock_picking_rel table")
    cr.execute("DROP TABLE account_move_stock_picking_rel")
    _logger.info("Creating new account_move_stock_picking_rel table via ORM")
    AccountMove = env["account.move"]
    registry._post_init_queue = deque()
    AccountMove._fields["picking_ids"].update_db(AccountMove, False)
    _logger.info("Filling account_move_stock_picking_rel relation table")
    cr.execute(
        """
        WITH query AS (
            SELECT aml.move_id, sm.picking_id
            FROM stock_move_invoice_line_rel
                LEFT JOIN account_move_line aml
                    ON aml.id = stock_move_invoice_line_rel.invoice_line_id
                LEFT JOIN stock_move sm
                    ON sm.id = stock_move_invoice_line_rel.move_id
            GROUP BY aml.move_id, sm.picking_id
        )
        INSERT INTO account_move_stock_picking_rel (account_move_id, stock_picking_id)
        SELECT * FROM query;
    """
    )
