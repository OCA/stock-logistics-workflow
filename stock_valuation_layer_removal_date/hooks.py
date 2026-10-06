# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists, create_column


def fill_removal_date(cr):
    cr.execute(
        """
        UPDATE stock_valuation_layer svl
        SET removal_date = agg.removal_date
        FROM (
            SELECT sml.move_id, MIN(lot.removal_date) AS removal_date
            FROM stock_move_line sml
            JOIN stock_lot lot ON lot.id = sml.lot_id
            WHERE sml.quantity != 0 AND lot.removal_date IS NOT NULL
            GROUP BY sml.move_id
        ) agg
        WHERE svl.stock_move_id = agg.move_id AND svl.lot_id IS NULL
        """
    )
    cr.execute(
        """
        UPDATE stock_valuation_layer svl
        SET removal_date = lot.removal_date
        FROM stock_lot lot
        WHERE lot.id = svl.lot_id AND lot.removal_date IS NOT NULL
        """
    )


def pre_init_hook(env):
    if column_exists(env.cr, "stock_valuation_layer", "removal_date"):
        return
    create_column(env.cr, "stock_valuation_layer", "removal_date", "timestamp")
    fill_removal_date(env.cr)
