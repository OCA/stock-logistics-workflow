# Copyright 2019 Tecnativa - David
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Speed up the installation of the module on an existing Odoo instance"""
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_move' AND
        column_name='qty_returnable'
    """)
    if not cr.fetchone():
        _logger.info('Creating field qty_returnable on stock_move')
        cr.execute("""
            ALTER TABLE stock_move ADD COLUMN qty_returnable float;
        """)
        cr.execute("""
            UPDATE stock_move SET qty_returnable = 0
            WHERE state IN ('draft', 'cancel')
        """)
        cr.execute("""
            UPDATE stock_move SET qty_returnable = product_uom_qty
            WHERE state = 'done'
        """)


def post_init_hook(cr, registry):
    """Set moves returnable qty on hand"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        moves_draft = env['stock.move'].search([
            ('state', 'in', ['draft', 'cancel'])
        ])
        moves_no_return_pendant = env['stock.move'].search([
            ('returned_move_ids', '=', False),
            ('state', 'not in', ['draft', 'cancel', 'done']),
        ])
        moves_by_reserved_availability = {}
        for move in moves_no_return_pendant:
            moves_by_reserved_availability.setdefault(
                move.reserved_availability, [])
            moves_by_reserved_availability[move.reserved_availability].append(
                move.id)
        for qty, ids in moves_by_reserved_availability.items():
            cr.execute(
                "UPDATE stock_move SET qty_returnable = %s "
                "WHERE id IN %s", (qty, tuple(ids)))
        moves_no_return_done = env['stock.move'].search([
            ('returned_move_ids', '=', False),
            ('state', '=', 'done'),
        ])
        # Recursively solve quantities
        updated_moves = (
            moves_no_return_done + moves_draft + moves_no_return_pendant)
        remaining_moves = env['stock.move'].search([
            ('returned_move_ids', '!=', False),
            ('state', '=', 'done'),
        ])
        while remaining_moves:
            _logger.info('{} moves left...'.format(len(remaining_moves)))
            remaining_moves, updated_moves = update_qty_returnable(
                cr, remaining_moves, updated_moves)


def update_qty_returnable(cr, remaining_moves, updated_moves):
    for move in remaining_moves:
        if all([x in updated_moves for x in move.returned_move_ids]):
            quantity_returned = sum(
                move.returned_move_ids.mapped('qty_returnable'))
            quantity = move.product_uom_qty - quantity_returned
            cr.execute(
                "UPDATE stock_move SET qty_returnable = %s "
                "WHERE id = %s", (quantity, move.id))
            remaining_moves -= move
            updated_moves += move
    return remaining_moves, updated_moves
