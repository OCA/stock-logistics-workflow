# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Fill the new field `picking_type_id` with the value of the field
    `picking_type`."""

    _logger.info("Filling the weight and volume fields")
    cr.execute(
        """
        UPDATE
            stock_picking set weight = total_weight_batch_picking,
            volume = total_volume_batch_picking
        WHERE
            total_weight_batch_picking is not null
            OR total_volume_batch_picking is not null
        """
    )
