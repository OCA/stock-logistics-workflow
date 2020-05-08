# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done_get_picking(self, moves, moves_todo):
        return moves_todo and moves_todo[0].picking_id or False
