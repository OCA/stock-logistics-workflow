# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _backdating_update_picking_date(self):
        """Set date_done as the youngest date among the done moves."""
        self.ensure_one()
        moves = self.move_lines
        done_moves = moves.filtered(
            lambda m: m.state == 'done'
        )
        dates = done_moves.mapped('date')
        if dates:
            self.date_done = max(dates)
        return True

    def _backdating_update_account_moves_date(self):
        """Set date on linked account.move same as date on stock.move."""
        self.ensure_one()
        stock_moves = self.move_lines
        picking_account_moves = self.env['account.move'].search(
            [
                ('stock_move_id', 'in', stock_moves.ids),
            ],
        )
        for stock_move in stock_moves:
            move_account_moves = picking_account_moves.filtered(
                lambda am: am.stock_move_id == stock_move
            )
            move_account_moves.update({
                'date': stock_move.date.date(),
            })
        return True

    @api.multi
    def action_done(self):
        result = super().action_done()
        for picking in self:
            picking._backdating_update_picking_date()
            picking._backdating_update_account_moves_date()
        return result

    # Disable pylint to match the exact signature in super
    # pylint: disable=dangerous-default-value
    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        # When a move needs backdating,
        # we are processing the moves of a picking one by one,
        # so we don't have to create a backorder if a move is missing
        if 'date_backdating' not in self.env.context:
            return super()._create_backorder(backorder_moves=backorder_moves)
