# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    This hook will initialize the computed columns that are added in the module.
    This is required to avoid the compute methods to be called by the orm during
    the module installation.
    """
    if not sql.column_exists(cr, "stock_picking", "assignation_max_weight"):
        _logger.info("Creating column assignation_max_weight into stock_picking")
        cr.execute(
            """
            ALTER TABLE stock_picking ADD COLUMN assignation_max_weight numeric;
        """
        )
        cr.execute(
            """
            UPDATE stock_picking
            SET assignation_max_weight = weight
            WHERE
                state not in ('done', 'cancel')
        """
        )
        _logger.info(f"{cr.rowcount} rows updated in stock_picking")
