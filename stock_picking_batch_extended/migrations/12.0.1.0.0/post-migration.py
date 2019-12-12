# Copyright 2019 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade
from psycopg2 import sql


def enable_oca_batch_validation(env):
    """We enable by default OCA behavior (which was the previous one) in all
    companies.
    """
    env['res.company'].search([]).write({'use_oca_batch_validation': True})


def copy_batch_pickings(env):
    src_column = openupgrade.get_legacy_name('batch_picking_id')
    openupgrade.logged_query(env.cr, sql.SQL(
        "ALTER TABLE stock_picking_batch ADD COLUMN {} INT4",
    ).format(sql.Identifier(src_column)))
    openupgrade.logged_query(env.cr, sql.SQL(
        """INSERT INTO stock_picking_batch (
            create_date, create_uid, write_date, write_uid,
            {}, name, state, date, user_id, notes,
            use_oca_batch_validation
        )
        SELECT
            src.create_date, src.create_uid, src.write_date, src.write_uid,
            src.id, src.name, src.state, src.date, src.picker_id, src.notes,
            True
        FROM stock_batch_picking src"""
    ).format(sql.Identifier(src_column)))
    openupgrade.logged_query(env.cr, sql.SQL(
        """UPDATE stock_picking sp
        SET batch_id = spb.id
        FROM stock_picking_batch spb
        WHERE spb.{} = sp.batch_picking_id"""
    ).format(sql.Identifier(src_column)))


@openupgrade.migrate()
def migrate(env, version):
    enable_oca_batch_validation(env)
    copy_batch_pickings(env)
