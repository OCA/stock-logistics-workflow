# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


class StockLandedCost(models.Model):

    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            if (move.product_id.valuation != 'real_time'
                    or move.product_id.cost_method not in ('fifo', 'average')
                    or move.state == 'cancel'):
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_("You cannot apply landed costs on the chosen "
                              "transfer(s). Landed costs can only be applied "
                              "for products with automated inventory valuation "
                              "and FIFO or AVCO costing method."))
        return lines
