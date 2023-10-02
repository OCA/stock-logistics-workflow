# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info("Creating column: delivery_count for table account_move")
    cr.execute(
        """
    ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS delivery_count INTEGER;
    """
    )
    logger.info("Populating values for column delivery_count in table account_move")
    cr.execute(
        """
        UPDATE account_move am SET delivery_count = t.delivery_count
        FROM (
            SELECT
                am.id AS account_move_id,
                COUNT(DISTINCT sm.picking_id) AS delivery_count
            FROM
                account_move am
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN stock_move_invoice_line_rel rel
                    ON rel.invoice_line_id = aml.id
                JOIN stock_move sm
                    ON sm.id = rel.move_id
            WHERE
                sm.picking_id IS NOT NULL
            GROUP BY
                am.id
        ) t
        WHERE am.id = t.account_move_id;
    """
    )
