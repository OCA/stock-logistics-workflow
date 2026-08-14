# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Initialize stage on existing lots based on their locked flag."""
    _logger.info("stock_lock_lot_stage: initializing stages on existing lots")
    Stage = env["stock.lot.stage"]
    unlocked_stage = Stage.search(
        [("locked", "=", False), ("approve_full_qty", "=", True)],
        limit=1,
    )
    locked_stage = Stage.search([("locked", "=", True)], limit=1)
    if not unlocked_stage or not locked_stage:
        _logger.warning("stock_lock_lot_stage: default stages not found, skipping init")
        return
    lots = env["stock.lot"].with_context(bypass_lock_permission_check=True)
    lots.search([("locked", "=", False)]).write({"stage_id": unlocked_stage.id})
    lots.search([("locked", "=", True)]).write({"stage_id": locked_stage.id})
