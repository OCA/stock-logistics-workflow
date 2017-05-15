# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the move will be automatically "
        "processed as soon as the products are available.")

    @api.multi
    def action_assign(self):
        super(StockMove, self).action_assign()
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(lambda m: m.state == 'assigned' and m.auto_move)
        todo_pickings = moves.mapped('picking_id')
        # We create packing operations to keep packing if any
        todo_pickings.do_prepare_partial()
        moves.action_done()

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


class StockLocationPath(models.Model):
    _inherit = 'stock.location.path'

    @api.model
    def _apply(self, move):
        """Set auto move to the new move created by push rule."""
        move.auto_move = self.auto == 'transparent'
        return super(StockLocationPath, self)._apply(move)
