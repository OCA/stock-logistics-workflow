# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields_list):
        """This method overwrites the functionality of the
            default_get(fields_list) for add the correct default
            quantity on the products of a return picking"""
        res = super().default_get(fields_list)
        if 'product_return_moves' not in res:
            return res
        return_line = self.env['stock.return.picking.line']
        for line_lst in res['product_return_moves']:
            move = self.env['stock.move'].browse(line_lst[2]['move_id'])
            line_lst[2]['quantity'] = return_line\
                .get_returned_restricted_quantity(move)
        return res

    def _create_returns(self):
        for return_line in self.product_return_moves:
            quantity = return_line.get_returned_restricted_quantity(
                return_line.move_id)
            if return_line.quantity > quantity:
                raise UserError(
                    _("Return more quantities than delivered is not allowed."))
        return super()._create_returns()


class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    @api.onchange('quantity')
    def _onchange_quantity(self):
        qty = self.get_returned_restricted_quantity(self.move_id)
        if self.quantity > qty:
            raise UserError(
                _("Return more quantities than delivered is not allowed."))

    @api.model
    def get_returned_restricted_quantity(self, stock_move):
        """This function is created to know how many products
            have the person who tries to create a return picking
            on his hand."""
        qty = stock_move.product_qty
        for line in stock_move.move_dest_ids.mapped('move_line_ids'):
            if line.state in {'partially_available', 'assigned'}:
                qty -= line.product_qty
            elif line.state == 'done':
                qty -= line.qty_done
        return qty
