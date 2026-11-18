# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    for column in ("product_customer_code", "product_customer_name"):
        if not column_exists(cr, "stock_move", column):
            create_column(cr, "stock_move", column, "varchar")
    cr.execute(
        """
        UPDATE stock_move sm
        SET product_customer_code = ci.product_code,
            product_customer_name = ci.product_name
        FROM (
            SELECT DISTINCT ON (move.id)
                move.id AS move_id,
                pci.product_code,
                pci.product_name
            FROM stock_move move
            JOIN stock_picking sp ON sp.id = move.picking_id
            JOIN res_partner rp ON rp.id = sp.partner_id
            JOIN product_product pp ON pp.id = move.product_id
            CROSS JOIN LATERAL (
                VALUES (rp.id), (rp.parent_id), (rp.commercial_partner_id)
            ) AS candidate(partner_id)
            JOIN product_customerinfo pci
                ON pci.partner_id = candidate.partner_id
                AND (
                    pci.product_id = pp.id
                    OR (
                        pci.product_id IS NULL
                        AND pci.product_tmpl_id = pp.product_tmpl_id
                    )
                )
            ORDER BY
                move.id,
                pci.product_id IS NULL,
                pci.sequence,
                pci.min_qty,
                pci.price,
                pci.id
        ) ci
        WHERE sm.id = ci.move_id
        """
    )
    _logger.info("Customer code and name set on %s stock moves", cr.rowcount)
