# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _create_extra_move(self):
        """
        When user set on stock move line done a quantity greater than initial
        demand Odoo creates an extra stock move with the difference and it is
        posible to create an extra stock move line with qty_done = 0 which will
        be deleted in _action_done method.
        This method set a context variable to prevent set qty_done for these
        cases.
        """
        my_self = self
        if self.picking_id.auto_fill_operation:
            my_self = self.with_context(skip_auto_fill_operation=True)
        return super(StockMove, my_self)._create_extra_move()

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """Auto-assign as done the quantity proposed for the lots"""
        res = super(StockMove, self)._prepare_move_line_vals(
            quantity, reserved_quant,
        )
        if (self.env.context.get('skip_auto_fill_operation') or
                not self.picking_id.auto_fill_operation):
            return res
        elif (self.picking_id.picking_type_id.avoid_lot_assignment and
              res.get('lot_id')):
            return res
        res.update({
            'qty_done': res.get('product_uom_qty', 0.0),
        })
        return res
