# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Pre-creating weighing state column to avoid computing everyone...")
    cr.execute("ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS weighing_state VARCHAR")


def post_init_hook(cr, registry):
    """Recompute weighing_state only in pending moves"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Computing weighing state on pending moves...")
    env["stock.move"].search(
        [
            ("has_weight", "=", True),
            ("state", "in", ("assigned", "confirmed", "waiting")),
        ]
    )._compute_weighing_state()
