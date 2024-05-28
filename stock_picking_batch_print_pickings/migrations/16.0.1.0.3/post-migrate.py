# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """
        UPDATE stock_picking_type
        SET print_documents_from_batch = 'pickings'
        WHERE batch_print_pickings IS NOT NULL
    """
    )
    _logger.info("Updated %s picking type", cr.rowcount)
