# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the move will be automatically "
        "processed as soon as the products are available.")

    @api.model
    def _get_auto_moves_by_pickings(self, auto_moves):
        """ Group moves by picking.
        @param auto_moves: stock.move data set
        @return dict dict of moves grouped by pickings
        {stock.picking(id): stock.move(id1, id2, id3 ...), ...}
        """
        auto_moves_by_pickings = dict()
        for move in auto_moves:
            if move.picking_id in auto_moves_by_pickings:
                auto_moves_by_pickings[move.picking_id] |= move
            else:
                auto_moves_by_pickings.update({move.picking_id: move})
        return auto_moves_by_pickings

    @api.multi
    def action_assign(self, no_prepare=False):

        already_assigned_moves = self.filtered(
            lambda m: m.state == 'assigned')

        not_assigned_auto_move = self - already_assigned_moves

        res = super(StockMove, self).action_assign(
            no_prepare=no_prepare)

        # Process only moves that have been processed recently
        auto_moves = not_assigned_auto_move.filtered(
            lambda m: m.state == 'assigned' and m.auto_move)

        # group the moves by pickings
        auto_moves_by_pickings = self._get_auto_moves_by_pickings(auto_moves)

        # process the moves by creating backorders
        self.env['stock.picking']._transfer_pickings_with_auto_move(
            auto_moves_by_pickings)
        return res

    @api.multi
    def _change_procurement_group(self):
        automatic_group = self.env.ref('stock_auto_move.automatic_group')
        moves = self.filtered(
            lambda m: m.auto_move and m.group_id != automatic_group)
        moves.write({'group_id': automatic_group.id})

    @api.multi
    def action_confirm(self):
        self._change_procurement_group()
        return super(StockMove, self).action_confirm()


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the generated move will be "
        "automatically processed as soon as the products are available. "
        "This can be useful for situations with chained moves where we "
        "do not want an operator action.")


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _get_stock_move_values(self):
        res = super(ProcurementOrder, self)._get_stock_move_values()
        if self.rule_id:
            res.update({'auto_move': self.rule_id.auto_move})
        return res
