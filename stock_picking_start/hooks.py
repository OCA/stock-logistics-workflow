# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Create and initialize the started field"""
    _logger.info("Create the started field")
    cr.execute(
        """
        ALTER TABLE stock_picking
        ADD COLUMN started boolean;
    """
    )
    _logger.info("Initialize the started field")
    cr.execute(
        """
        UPDATE stock_picking
        SET started = printed
        WHERE state = 'assigned';
    """
    )
    _logger.info(f"{cr.rowcount} records updated")
