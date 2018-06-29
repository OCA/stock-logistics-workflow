# Copyright 2013-2015 Camptocamp SA - Nicolas Bessi
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        for picking in self:

            # Check the picking state and condition before splitting
            if picking.state == 'draft':
                raise UserError(_('Mark as todo this picking please.'))
            if all([x.qty_done == 0.0 for x in picking.move_line_ids]):
                raise UserError(
                    _('You must enter done quantity in order to split your '
                      'picking in several ones.'))

            # Split moves considering the qty_done on moves
            new_moves = self.env['stock.move']
            qty_done_per_product = {}
            for move in picking.move_lines:
                rounding = move.product_uom.rounding
                qty_done = move.quantity_done
                qty_initial = move.product_uom_qty
                qty_diff_compare = float_compare(
                    qty_done, qty_initial, precision_rounding=rounding
                )
                if qty_diff_compare < 0:
                    qty_split = qty_initial - qty_done
                    qty_uom_split = move.product_uom._compute_quantity(
                        qty_split,
                        move.product_id.uom_id,
                        rounding_method='HALF-UP'
                    )
                    new_move_id = move._split(qty_uom_split)
                    new_moves |= self.env['stock.move'].browse(new_move_id)
                if qty_done:
                    for move_line in move.move_line_ids:
                        if move_line.product_qty and move_line.qty_done:
                            # To avoid an error
                            # when picking is partially available
                            try:
                                move_line.write(
                                    {'product_uom_qty': move_line.qty_done})
                                product = move_line.product_id
                                qty_done_per_product[product.id] = \
                                    move_line.qty_done
                            except UserError:
                                pass

            # If we have new moves to move, create the backorder picking
            if new_moves:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                })
                picking.message_post(
                    _(
                        'The backorder <a href="#" '
                        'data-oe-model="stock.picking" '
                        'data-oe-id="%d">%s</a> has been created.'
                    ) % (
                        backorder_picking.id,
                        backorder_picking.name
                    )
                )
                new_moves.write({
                    'picking_id': backorder_picking.id,
                })
                new_moves.mapped('move_line_ids').write({
                    'picking_id': backorder_picking.id,
                })
                new_moves._action_assign()

                # Propagate split to chained picking/moves

                chained_moves = self.env['stock.move']
                for move in picking.move_lines:
                    # Only take into account single chained moves
                    if len(move.move_dest_ids) == 1:
                        chained_moves |= move.move_dest_ids

                chained_picking = chained_moves.mapped('picking_id') \
                    if chained_moves else None

                # The chained moves should be related to the same picking.
                if chained_picking and len(chained_picking) == 1:
                    chained_picking.action_assign()
                    need_split = False
                    for chained_move in chained_moves:
                        for move_line in chained_move.move_line_ids:
                            product = move_line.product_id
                            if product.id in qty_done_per_product:
                                need_split = True
                                qty_done = qty_done_per_product[product.id]
                                move_line.write({
                                    'qty_done': qty_done,
                                    'product_uom_qty': qty_done,
                                })
                    if need_split:
                        chained_picking.split_process()
