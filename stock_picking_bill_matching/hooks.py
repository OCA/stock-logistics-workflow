# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)

# (table, column, sql type, neutral value)
#
# The neutral value is the one the compute methods produce for an unmatched
# record: nothing is matched, nothing is left to match.
COMPUTED_COLUMNS = (
    ("account_move", "is_picking_matched", "boolean", "false"),
    ("account_move_line", "unmatched_qty", "numeric", "0"),
    ("stock_picking", "is_picking_matched", "boolean", "false"),
    ("stock_move", "unmatched_qty", "numeric", "0"),
    ("purchase_order", "is_picking_matched", "boolean", "false"),
)


def pre_init_hook(cr):
    """Create the stored computed columns before Odoo does.

    Odoo computes a NEW stored computed field for every row that already exists
    when it creates its column (``Prepare computation of ...`` followed by one
    UPDATE over the whole table). On a database with millions of ``stock_move``
    and ``account_move_line`` rows that is tens of minutes inside the install
    transaction: the whole install holds its locks, and a worker killed on a
    timeout rolls it all back.

    A column that already exists is left alone - Odoo only computes when it
    creates the column - so creating them here with their neutral value turns
    the install into a metadata-only operation. The values are then recomputed
    per record by the compute methods as soon as the record is written, which is
    what the matching screens do before they read them; a database that needs the
    historical values immediately can force a recompute
    (``<model>.search([])._compute_<field>()``) outside the install.

    ``ADD COLUMN ... DEFAULT`` is metadata-only on PostgreSQL 11+, so the default
    stays in place: Odoo always writes the column itself and the old rows keep
    reading the neutral value instead of NULL.
    """
    for table, column, sql_type, default in COMPUTED_COLUMNS:
        _logger.info(
            "stock_picking_bill_matching: pre-creating %s.%s", table, column
        )
        cr.execute(
            f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS '
            f'"{column}" {sql_type} DEFAULT {default}'
        )
