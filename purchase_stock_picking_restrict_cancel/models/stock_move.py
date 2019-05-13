# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def identify_blocking_objects(self, blocking_moves):
        res = super().identify_blocking_objects(blocking_moves)
        purchases = blocking_moves.mapped('created_purchase_line_id')
        if purchases:
            res.update({'purchases': purchases})
        return res
