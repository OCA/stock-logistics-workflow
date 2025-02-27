# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import tools

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    migrate_from_stock_picking_type_shipping_policy(env)


def migrate_from_stock_picking_type_shipping_policy(env):
    _logger.info("Migrate from 'stock_picking_type_shipping_policy'...")
    # Odoo 18.0 comes with a new '<stock.picking.type>.move_type' field set
    # by default to 'direct' (= As soon as possible).
    # If the current module is installed, we want this field set with the
    # value that was configured in old 'shipping_policy' field.
    if tools.sql.column_exists(env.cr, "stock_picking_type", "shipping_policy"):
        queries = [
            """
                UPDATE stock_picking_type
                SET force_move_type=true, move_type='direct'
                WHERE shipping_policy='force_as_soon_as_possible';
            """,
            """
                UPDATE stock_picking_type
                SET force_move_type=true, move_type='one'
                WHERE shipping_policy='force_all_products_ready';
            """,
        ]
        for query in queries:
            env.cr.execute(query)
