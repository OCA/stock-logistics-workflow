# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)

# Tables carrying the legacy ``actual_date`` document field (a fixed, trusted
# whitelist - used directly in SQL below).
_LEGACY_DOC_TABLES = ("stock_picking", "stock_scrap")


def pre_init_hook(env):
    if not column_exists(env.cr, "stock_picking", "actual_date"):
        return
    _logger.info("stock_date_done: migrating data from stock_move_actual_date")
    _create_origin_columns(env)
    _backfill_date_done(env)


def post_init_hook(env):
    if not column_exists(env.cr, "stock_picking", "actual_date"):
        return
    _migrate_group_membership(env)


def _create_origin_columns(env):
    for table in _LEGACY_DOC_TABLES:
        if not column_exists(env.cr, table, "origin_date_done"):
            # Datetime -> timestamp (without time zone), as Odoo stores it.
            env.cr.execute(f"ALTER TABLE {table} ADD COLUMN origin_date_done timestamp")


def _backfill_date_done(env):
    for table in _LEGACY_DOC_TABLES:
        if not column_exists(env.cr, table, "actual_date"):
            continue
        env.cr.execute(
            f"""
            UPDATE {table}
            SET origin_date_done = date_done
            WHERE date_done IS NOT NULL
              AND origin_date_done IS NULL
            """
        )
        env.cr.execute(
            f"""
            UPDATE {table}
            SET date_done = actual_date + date_done::time
            WHERE actual_date IS NOT NULL
              AND date_done IS NOT NULL
              AND actual_date <> date_done::date
            """
        )


def _migrate_group_membership(env):
    old_group = env.ref(
        "stock_move_actual_date.group_actual_date_editable",
        raise_if_not_found=False,
    )
    new_group = env.ref(
        "stock_date_done.group_date_done_editable", raise_if_not_found=False
    )
    if old_group and new_group and old_group.user_ids:
        new_group.user_ids = [(4, uid) for uid in old_group.user_ids.ids]
