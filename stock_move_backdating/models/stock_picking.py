# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        result = super(StockPicking, self).do_transfer()
        for picking in self:
            # set date_done as the youngest date among the moves
            dates = picking.move_lines.filtered(
                lambda m: m.state == 'done').mapped('date')
            picking.write({'date_done': max(dates)})
            all_moves = self.env['account.move'].search(
                [('ref', '=', picking.name),
                 ('line_ids.name', 'in', picking.mapped('move_lines.name'))])
            for move in picking.move_lines:
                for account_move in all_moves.filtered(
                        lambda m, pm=move: pm.name in m.line_ids.mapped('name')
                ):
                    # set date on account.move same as date on stock.move
                    account_move.date = move.date
        return result
