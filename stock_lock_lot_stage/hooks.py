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
    # Assign stages with SQL: reading or writing stock.lot through the ORM
    # would recompute the stored `locked` field and run its constraints while
    # lots still have no stage, which fails on lots with reserved quantities.
    env.cr.execute(
        "UPDATE stock_lot SET stage_id = %s WHERE locked IS TRUE",
        (locked_stage.id,),
    )
    env.cr.execute(
        "UPDATE stock_lot SET stage_id = %s WHERE locked IS NOT TRUE",
        (unlocked_stage.id,),
    )
