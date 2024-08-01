# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_backdating = fields.Datetime(
        string='Forced Effective Date',
        help="The Actual Movement Date of the Operations "
             "only if they have all the same value.",
        compute='_compute_date_backdating',
        store=True,
    )

    @api.depends(
        'move_line_ids.date_backdating',
    )
    def _compute_date_backdating(self):
        for picking in self:
            move_lines = picking.move_line_ids
            move_lines_back_dates = move_lines.mapped('date_backdating')
            move_lines_back_date = set(move_lines_back_dates)
            if len(move_lines_back_date) == 1:
                date_backdating = move_lines_back_date.pop()
            else:
                date_backdating = False
            picking.date_backdating = date_backdating

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
        stock_moves._backdating_account_moves()
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
