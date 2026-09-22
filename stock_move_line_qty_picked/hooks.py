# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def initialize_picked_quantities(cr):
    # Preserve existing partial scans when adopting a column from another addon.
    cr.execute(
        "ALTER TABLE stock_move_line ADD COLUMN IF NOT EXISTS qty_picked numeric"
    )
    cr.execute(
        """
        UPDATE stock_move_line
           SET qty_picked = CASE WHEN picked OR state = 'done' THEN quantity ELSE 0 END
         WHERE qty_picked IS NULL
            OR (qty_picked = 0 AND (picked OR state = 'done') AND quantity != 0)
        """
    )
    cr.execute(
        """
        UPDATE stock_move_line SET picked = TRUE
         WHERE qty_picked > 0 AND NOT picked AND state NOT IN ('done', 'cancel');
        UPDATE stock_move m SET picked = TRUE
         WHERE NOT m.picked AND m.state NOT IN ('done', 'cancel')
           AND EXISTS (SELECT 1 FROM stock_move_line ml
                        WHERE ml.move_id = m.id AND ml.picked)
        """
    )


def pre_init_hook(env):
    initialize_picked_quantities(env.cr)
