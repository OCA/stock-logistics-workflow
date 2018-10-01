# -*- coding: utf-8 -*-
# © 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""
from openerp import api, fields, models, _


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    # Change label of that field to use it for split
    qty_done = fields.Float('Done or split')


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def do_split(self):
        """ Split picking according to stock operations """
        move_model = self.env['stock.move']
        for picking in self:
            prod2move_ids = {}
            moves2split = []
            moves4backorder = self.env['stock.move'].browse()
            for move in [x for x in picking.move_lines if x.state not in
                         ('done', 'cancel')]:
                if not prod2move_ids.get(move.product_id.id):
                    prod2move_ids[move.product_id.id] = [move]
                else:
                    prod2move_ids[move.product_id.id].append(move)

            for ops in picking.pack_operation_ids:
                if ops.product_id.id and ops.qty_done:
                    qty_done = ops.qty_done

                    for move in prod2move_ids.get(ops.product_id.id, []):
                        if move.product_qty <= qty_done:
                            moves4backorder |= move
                            qty_done -= move.product_qty
                        else:
                            moves2split.append((move, qty_done))
                            qty_done = 0
                        if qty_done:
                            break

            for move, qty in moves2split:
                new_move = move_model.split(move, qty)
                moves4backorder |= move_model.browse(new_move)

            if moves4backorder:
                backorder = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'pack_operation_ids': [],
                    'backorder_id': picking.id,
                })
                picking.message_post(
                    body=_("Back order <em>%s</em> <b>created</b>."
                           ) % (backorder.name))
                moves4backorder.write({'picking_id': backorder.id})

                # Re generate operations
                backorder.recheck_availability()
                picking.recheck_availability()
        return True
