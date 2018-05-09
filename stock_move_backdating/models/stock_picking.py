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
            dates = picking.mapped('move_lines.date')
            picking.write({'date_done': max(dates)})
            for move in picking.move_lines:
                # set date on account.move same as date on stock.move
                account_moves = self.env['account.move'].search(
                    [('ref', '=', picking.name),
                     ('line_ids.name', '=', move.name)])
                for account_move in account_moves:
                    account_move.date = move.date
        return result
