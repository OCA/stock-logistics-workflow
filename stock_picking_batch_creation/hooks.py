# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def _create_and_init_nbr_picking_lines_column(cr):
    """Create and initialize the column nbr_picking_lines in the table
    stock_picking

    It's used to create and initialize the column nbr_picking_lines in the
    table stock_picking. To avoid to freeze the database during the
    installation of the module, this column is initialized only for the pickings
    that are not in state done or cancel
    """
    _logger.info("Create the column nbr_picking_lines in the table stock_picking")
    if not column_exists(cr, "stock_picking", "nbr_picking_lines"):
        create_column(cr, "stock_picking", "nbr_picking_lines", "integer")

    _logger.info("Initialize the column nbr_picking_lines")
    cr.execute(
        """
        UPDATE stock_picking
        SET nbr_picking_lines = (
            SELECT count(1)
            FROM stock_move_line
            WHERE picking_id = stock_picking.id
        )
        Returning id
        """
    )
    updated_pickings = cr.fetchall()
    _logger.info(
        "The column nbr_picking_lines has been initialized for %s pickings",
        len(updated_pickings),
    )


def pre_init_hook(cr):
    """This method is called before the module is installed"""
    _create_and_init_nbr_picking_lines_column(cr)
