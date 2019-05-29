# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def identify_blocking_objects(self, blocking_moves):
        res = super().identify_blocking_objects(blocking_moves)
        workorders = blocking_moves.mapped('production_id')
        if workorders:
            res.update({'workorders': workorders})
        return res
