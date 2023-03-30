# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)

NBR_MONTHS = 2


def pre_init_hook(cr):
    """Initialize the first_move_id and the first_picking_type_id columns
    on the stock_move table to avoid performance issues during the module
    installation.

    Since these new columns are probably not used by your process on old
    stock_move we limit the computation to the stock_move that are created
    for the last 12 months.
    """
    if not sql.column_exists(cr, "stock_move", "first_move_id"):
        _logger.info("Creating column first_move_id into stock_move")
        cr.execute(
            """
            ALTER TABLE stock_move ADD COLUMN first_move_id integer;
            """
        )
        # The first move id is the id of the first move that initiated the
        # chain of moves. With a push rule, the first move is the move that
        # is the first into the origin_ids field of the move.
        # With a pull rule, the first move is the move that is the last into
        # the move_dest_ids field of the move.

        _logger.info(
            f"Computing first_move_id on pull action for the last {NBR_MONTHS} months"
        )
        # process pull
        cr.execute(
            """
            -- Get the last move_dest_id into the path from move_orig_id to
            -- move_dest_id into table stock_move_move_rel
            WITH RECURSIVE move_chain AS (
                  SELECT move_orig_id, move_dest_id, 1 AS chain_length
                  FROM stock_move_move_rel
                     JOIN stock_move sm on sm.id = move_orig_id
                         AND sm.create_date > now() - interval '%s months'
                  UNION ALL

                  SELECT mc.move_orig_id, smmr.move_dest_id, mc.chain_length + 1
                  FROM move_chain mc
                  JOIN stock_move_move_rel smmr
                    ON mc.move_dest_id = smmr.move_orig_id
            ),
            last_move_dest_id AS (
                SELECT move_orig_id, move_dest_id
                FROM (
                    SELECT move_orig_id, move_dest_id, ROW_NUMBER() OVER (
                        PARTITION BY move_orig_id ORDER BY chain_length DESC
                    ) AS rn
                    FROM move_chain
                ) AS subquery
                WHERE rn = 1
            )
            -- We can now update moves created by a 'pull' action
            UPDATE stock_move
                set first_move_id = move_dest_id
            FROM
                last_move_dest_id,
                stock_rule sr
            WHERE
               last_move_dest_id.move_orig_id = stock_move.id
               AND sr.id = stock_move.rule_id
               AND sr.action = 'pull'
            AND stock_move.create_date > now() - interval '%s months'
        """,
            (NBR_MONTHS, NBR_MONTHS),
        )
        _logger.info(f"{cr.rowcount} row updated to set first_move_id on pull action")

        _logger.info(
            f"Computing first_move_id on push action for the last {NBR_MONTHS} months"
        )
        # process push
        cr.execute(
            """
            -- Get the first move_orig_id into the path from move_dest_id to
            -- move_orig_id_id into table stock_move_move_rel
            WITH RECURSIVE move_chain AS (
                  SELECT move_dest_id, move_orig_id, 1 AS chain_length
                  FROM stock_move_move_rel
                  JOIN stock_move sm on sm.id = move_dest_id
                         AND sm.create_date > now() - interval '%s months'

                  UNION ALL

                  SELECT smmr.move_dest_id, mc.move_orig_id, mc.chain_length + 1
                  FROM move_chain mc
                  JOIN stock_move_move_rel smmr
                    ON mc.move_orig_id = smmr.move_dest_id
            ),
            first_move_orig_id AS (
                SELECT move_dest_id, move_orig_id
                FROM (
                    SELECT move_dest_id, move_orig_id, ROW_NUMBER() OVER (
                        PARTITION BY move_dest_id ORDER BY chain_length DESC
                    ) AS rn
                    FROM move_chain
                ) AS subquery
                WHERE rn = 1
            )
            -- We can now update moves created by a 'pull' action
            UPDATE stock_move
                set first_move_id = move_orig_id
            FROM
                first_move_orig_id,
                stock_rule sr
            WHERE
               first_move_orig_id.move_dest_id = stock_move.id
               AND sr.id = stock_move.rule_id
               AND sr.action = 'push'
               -- we limit to the move created in the last 12 months
               AND stock_move.create_date > now() - interval '%s months'

        """,
            (NBR_MONTHS, NBR_MONTHS),
        )
        _logger.info(f"{cr.rowcount} row updated to set first_move_id on push action")

        _logger.info(
            f"Initializing first_move_id for the last {NBR_MONTHS} months"
            f" with the move id itself if not set."
        )
        cr.execute(
            """
            UPDATE stock_move
            SET first_move_id = id
            WHERE first_move_id IS NULL
            AND create_date > now() - interval '%s months'
        """,
            (NBR_MONTHS,),
        )

    if not sql.column_exists(cr, "stock_move", "first_picking_type_id"):
        _logger.info("Creating column first_picking_type_id into stock_move")
        cr.execute(
            """
            ALTER TABLE stock_move ADD COLUMN first_picking_type_id integer;
            """
        )
        _logger.info(
            "Initializing first_picking_type_id for stock_move with a first_move_id"
        )
        cr.execute(
            """
            UPDATE stock_move
            SET first_picking_type_id = sm.first_picking_type_id
            FROM stock_move sm
            WHERE sm.id = stock_move.first_move_id
            AND stock_move.first_picking_type_id IS NULL
        """
        )
        _logger.info(f"{cr.rowcount} row updated to set first_picking_type_id")
