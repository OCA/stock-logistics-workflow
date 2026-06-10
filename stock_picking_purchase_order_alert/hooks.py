import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    cr.execute(
        """ALTER TABLE stock_picking ADD COLUMN IF NOT
        EXISTS has_quantity_alert BOOLEAN DEFAULT FALSE"""
    )
    cr.execute(
        """ALTER TABLE stock_picking ADD COLUMN IF NOT
        EXISTS quantity_alert_message TEXT"""
    )
    logger.info("Pre-init hook executed")


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    pickings = env["stock.picking"].search(
        [
            ("state", "not in", ["cancel", "done"]),
            ("purchase_id", "!=", False),
        ]
    )
    pickings._compute_has_quantity_alert()
    logger.info("Post-init hook executed")
