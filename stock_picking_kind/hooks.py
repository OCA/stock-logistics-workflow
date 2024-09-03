# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Initialize picking_kind field based on location_id and location_dest_id"""
    if not sql.column_exists(env.cr, "stock_picking", "picking_kind"):
        _logger.info("Create picking_kind column")
        env.cr.execute(
            """
            ALTER TABLE stock_picking
            ADD COLUMN picking_kind character varying;
        """
        )
        _logger.info("Initialize picking_kind field")
        env.cr.execute(
            """
            UPDATE stock_picking
            SET picking_kind = (
                CASE
                    WHEN
                        origin.usage = 'supplier'
                        AND destination.usage = 'customer'
                    THEN 'drop_shipping'
                    WHEN
                        origin.usage = 'customer'
                        AND destination.usage = 'supplier'
                    THEN 'drop_shipping_return'
                    WHEN
                        origin.usage = 'customer'
                        AND destination.usage != 'customer'
                    THEN 'customer_return'
                    WHEN
                        origin.usage != 'customer'
                        AND destination.usage = 'customer'
                    THEN 'customer_out'
                    WHEN
                        origin.usage = 'supplier'
                        AND destination.usage != 'supplier'
                    THEN 'supplier_in'
                    WHEN
                        origin.usage != 'supplier'
                        AND destination.usage = 'supplier'
                    THEN 'supplier_return'
                    ELSE NULL
                END
            )
            FROM stock_location origin, stock_location destination
            WHERE stock_picking.location_id = origin.id
            AND stock_picking.location_dest_id = destination.id
        """
        )
        _logger.info(f"{env.cr.rowcount} rows updated")
