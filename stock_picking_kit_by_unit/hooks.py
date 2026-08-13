# Copyright (C) 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Create kit_product_id column to avoid slow ORM recompute on upgrade."""
    _logger.info("stock_picking_kit_by_unit: pre-init creating kit_product_id column")
    env.cr.execute("""
        ALTER TABLE stock_move_line
        ADD COLUMN IF NOT EXISTS kit_product_id INTEGER
    """)


def post_init_hook(env):
    """Populate kit_product_id for open pickings using the ORM compute method."""
    _logger.info(
        "stock_picking_kit_by_unit: populating kit_product_id for open pickings"
    )
    lines = env["stock.move.line"].search(
        [
            ("picking_id.state", "not in", ["done", "cancel"]),
            ("move_id.bom_line_id", "!=", False),
            ("kit_product_id", "=", False),
        ]
    )
    lines._compute_kit_product_id()
    _logger.info(
        "stock_picking_kit_by_unit: kit_product_id populated for %d lines", len(lines)
    )
