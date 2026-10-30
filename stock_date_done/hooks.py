# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)

# Tables carrying the legacy ``actual_date`` document field (a fixed, trusted
# whitelist - used directly in SQL below).
_LEGACY_DOC_TABLES = {"stock_picking": "picking_id", "stock_scrap": "scrap_id"}


def pre_init_hook(env):
    _create_origin_columns(env)
    _backfill_origin_date_done(env)
    if not column_exists(env.cr, "stock_picking", "actual_date"):
        return
    _logger.info("stock_date_done: migrating data from stock_move_actual_date")
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


def _backfill_origin_date_done(env):
    for table in _LEGACY_DOC_TABLES:
        env.cr.execute(
            f"""
            UPDATE {table}
            SET origin_date_done = date_done
            WHERE date_done IS NOT NULL
              AND origin_date_done IS NULL
            """
        )


def _backfill_date_done(env):
    for table, move_column in _LEGACY_DOC_TABLES.items():
        if not column_exists(env.cr, table, "actual_date"):
            continue
        # actual_date is a local date; assume the company's timezone.
        env.cr.execute(
            f"""
            WITH doc AS (
                SELECT d.id,
                    d.actual_date,
                    d.date_done AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(p.tz, 'UTC') AS local_done,
                    COALESCE(p.tz, 'UTC') AS tz
                FROM {table} d
                JOIN res_company c ON c.id = d.company_id
                JOIN res_partner p ON p.id = c.partner_id
                WHERE d.actual_date IS NOT NULL
                  AND d.date_done IS NOT NULL
            )
            UPDATE {table} t
            SET date_done = (doc.actual_date + doc.local_done::time)
                AT TIME ZONE doc.tz AT TIME ZONE 'UTC'
            FROM doc
            WHERE t.id = doc.id
              AND doc.actual_date <> doc.local_done::date
            """
        )
        env.cr.execute(
            f"""
            UPDATE {table} t
            SET date_done = (t.actual_date + time '12:00')
                AT TIME ZONE COALESCE(p.tz, 'UTC') AT TIME ZONE 'UTC'
            FROM res_company c
            JOIN res_partner p ON p.id = c.partner_id
            WHERE c.id = t.company_id
              AND t.actual_date IS NOT NULL
              AND t.date_done IS NULL
              AND t.state NOT IN ('done', 'cancel')
            """
        )
        env.cr.execute(
            f"""
            UPDATE stock_move m
            SET date = t.date_done
            FROM {table} t
            WHERE m.{move_column} = t.id
              AND m.state = 'done'
              AND t.date_done <> t.origin_date_done
            """
        )
        env.cr.execute(
            f"""
            UPDATE stock_move_line ml
            SET date = m.date
            FROM stock_move m
            JOIN {table} t ON m.{move_column} = t.id
            WHERE ml.move_id = m.id
              AND m.state = 'done'
              AND t.date_done <> t.origin_date_done
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
