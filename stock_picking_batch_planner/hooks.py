# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tools.sql import column_exists, create_column


def pre_init_hook(env):
    # Create the missing columns `auto_batch_original` and `plan_batch`
    if not column_exists(env.cr, "stock_picking_type", "auto_batch_original"):
        create_column(env.cr, "stock_picking_type", "auto_batch_original", "boolean")
    if not column_exists(env.cr, "stock_picking_type", "plan_batch"):
        create_column(env.cr, "stock_picking_type", "plan_batch", "boolean")
    env.cr.execute("""
        UPDATE stock_picking_type
        SET auto_batch_original = auto_batch, plan_batch = auto_batch
    """)


def uninstall_hook(env):
    # Restore the value of `auto_batch` with the value of `auto_batch_original`
    if not column_exists(env.cr, "stock_picking_type", "auto_batch"):
        create_column(env.cr, "stock_picking_type", "auto_batch", "boolean")
    env.cr.execute("""UPDATE stock_picking_type SET auto_batch = auto_batch_original""")
