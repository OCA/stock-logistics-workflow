# -*- coding: utf8 -*-
#
# Copyright (C) 2014 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp import api, fields, models


class stock_auto_move_move(models.Model):
    _inherit = "stock.move"

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the move will be automatically "
        "processed as soon as the products are available.")

    @api.multi
    def action_assign(self):
        super(stock_auto_move_move, self).action_assign()
        # picking_env = self.env['stock.picking']
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(lambda m: m.state == 'assigned' and m.auto_move)
        picking_ids = {m.picking_id.id for m in moves}
        todo_pickings = self.env['stock.picking'].browse(picking_ids)
        # We create packing operations to keep packing if any
        todo_pickings.do_prepare_partial()
        moves.action_done()

    @api.multi
    def action_confirm(self):
        automatic_group = self.env.ref('stock_auto_move.automatic_group')
        for move in self:
            if move.auto_move and move.group_id != automatic_group:
                move.group_id = automatic_group
        return super(stock_auto_move_move, self).action_confirm()


class stock_auto_move_procurement_rule(models.Model):
    _inherit = 'procurement.rule'

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the generated move will be "
        "automatically processed as soon as the products are available. "
        "This can be useful for situations with chained moves where we "
        "do not want an operator action.")


class stock_auto_move_procurement(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        res = super(stock_auto_move_procurement, self)._run_move_create(
            procurement)
        res.update({'auto_move': procurement.rule_id.auto_move})
        return res


class stock_auto_move_location_path(models.Model):
    _inherit = 'stock.location.path'

    @api.model
    def _prepare_push_apply(self, rule, move):
        """Set auto move to the new move created by push rule."""
        res = super(stock_auto_move_location_path, self)._prepare_push_apply(
            rule, move)
        res.update({
            'auto_move': (rule.auto == 'auto'),
        })
        return res
