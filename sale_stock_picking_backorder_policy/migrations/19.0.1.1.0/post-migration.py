# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Copy the partner policy from stock_picking_backorder_policy.

    The ``res.partner.backorder_policy`` field used to be defined by
    ``stock_picking_backorder_policy``. It moved here as
    ``sale_backorder_policy``, to leave room for a purchase counterpart.

    The old column is still around at this point: Odoo only drops the column
    of a removed field at the very end of the loading process.
    """
    if not column_exists(cr, "res_partner", "backorder_policy"):
        return
    cr.execute(
        """
        UPDATE res_partner
        SET sale_backorder_policy = backorder_policy
        WHERE backorder_policy IS NOT NULL
        """
    )
