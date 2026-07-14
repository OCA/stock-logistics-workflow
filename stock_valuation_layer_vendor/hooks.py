# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists, create_column


def pre_init_hook(env):
    if column_exists(env.cr, "stock_valuation_layer", "vendor_id"):
        return
    create_column(env.cr, "stock_valuation_layer", "vendor_id", "int4")
    env.cr.execute(
        """
        UPDATE stock_valuation_layer svl
        SET vendor_id = pol.partner_id
        FROM stock_move sm
        JOIN purchase_order_line pol ON pol.id = sm.purchase_line_id
        WHERE svl.stock_move_id = sm.id
        """
    )
