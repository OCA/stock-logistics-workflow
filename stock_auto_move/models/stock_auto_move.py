# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the move will be automatically "
        "processed as soon as the products are available.")

    @api.multi
    def action_assign(self):
        super(StockMove, self).action_assign()
        # picking_env = self.env['stock.picking']
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(lambda m: m.state == 'assigned' and m.auto_move)
        todo_pickings = moves.mapped('picking_id')
        # We create packing operations to keep packing if any
        todo_pickings.do_prepare_partial()
        moves.action_done()

    @api.multi
    def _change_procurement_group(self):
        automatic_group = self.env.ref('stock_auto_move.automatic_group')
        for move in self:
            if move.auto_move and move.group_id != automatic_group:
                move.group_id = automatic_group

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

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(
            procurement)
        res.update({'auto_move': procurement.rule_id.auto_move})
        return res


class StockLocationPath(models.Model):
    _inherit = 'stock.location.path'

    @api.model
    def _prepare_push_apply(self, rule, move):
        """Set auto move to the new move created by push rule."""
        res = super(StockLocationPath, self)._prepare_push_apply(
            rule, move)
        res.update({
            'auto_move': (rule.auto == 'auto'),
        })
        return res
