# Copyright 2024 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Declare procurement group linked to more than one sale order as
    # merged for procurement groups linked to stock pickings of type outgoing
    SQL = """
        UPDATE
            procurement_group
        SET
            is_merged = TRUE
        WHERE
            id IN (
                SELECT
                    procurement_group_id
                FROM
                    procurement_group_sale_order_rel
                    JOIN stock_picking ON stock_picking.group_id = procurement_group_id
                WHERE
                    stock_picking.state NOT IN ('cancel', 'done')
                    AND stock_picking.picking_type_id = 4
                GROUP BY
                    procurement_group_id
                HAVING
                    COUNT(DISTINCT sale_order_id) > 1
            )
    """
    env.cr.execute(SQL)
    _logger.info("Declared %d procurement groups as merged", env.cr.rowcount)

    # Get all procurement group linked to only one sale order for stock pickings
    # of type outgoing with state not done or cancel and not set as merged.
    SQL = """
    SELECT
        id
    FROM stock_picking
    WHERE
        state NOT IN ('cancel', 'done')
        AND picking_type_id = 4
        AND group_id IN (
            SELECT
                procurement_group_id
            FROM
                procurement_group_sale_order_rel
                JOIN stock_picking ON stock_picking.group_id = procurement_group_id
                JOIN procurement_group ON procurement_group.id = procurement_group_id
            WHERE
                stock_picking.state NOT IN ('cancel', 'done')
                AND stock_picking.picking_type_id = 4
                AND (not procurement_group.is_merged or procurement_group.is_merged IS NULL)
            GROUP BY
                procurement_group_id
            HAVING
                COUNT(DISTINCT sale_order_id) = 1
        )
    """
    env.cr.execute(SQL)
    ids = [row[0] for row in env.cr.fetchall()]
    # generate a merged procurement group for each group of stock pickings
    pickings = env["stock.picking"].browse(ids)
    total = len(pickings)
    cpt = 0
    for picking in pickings:
        cpt += 1
        base_group = picking.group_id
        moves = picking.move_ids.filtered(
            lambda move: move.state not in ("done", "cancel")
        )
        _logger.info(
            "Generating a merged procurement group for stock picking %s (%d of %d)",
            picking.name,
            cpt,
            total,
        )
        assert len(moves.group_id) == 1
        group_pickings = moves.group_id.picking_ids.filtered(
            lambda picking: not (picking.printed or picking.state == "done")
        )
        moves = group_pickings.move_ids
        new_group = base_group.copy(
            picking._prepare_merge_procurement_group_values(moves.original_group_id)
        )
        moves.group_id = new_group
