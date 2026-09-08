# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Start the backfill of the existing valuation layers.

    The cron is shipped inactive so that it stays inactive once it has drained
    the backlog and deactivated itself (the data file is noupdate).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref(
        "stock_valuation_fifo_lot_allocation.ir_cron_lot_allocation_backfill"
    ).active = True
