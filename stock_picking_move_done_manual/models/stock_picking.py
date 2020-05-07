# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    allow_stock_picking_move_done_manual = fields.Boolean(
        related='picking_type_id.allow_stock_picking_move_done_manual')

    def _button_validate_get_no_quantities_done(self):
        no_quantities_done = super(
            StockPicking, self)._button_validate_get_no_quantities_done()
        precision_digits = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        # If we have already started to process this picking and we want
        # to validate it.
        done = any(m.state == 'done' for m in self.move_lines) and \
            any(float_is_zero(
                move_line.qty_done,
                precision_digits=precision_digits) for move_line in
                self.move_line_ids.filtered(lambda m: m.state != 'done'))
        if done:
            return False
        return no_quantities_done

    def _validate_get_no_reserved_quantities(self):
        no_reserved_quantities = super(
            StockPicking, self)._validate_get_no_reserved_quantities()
        # If we have already started to process this picking and we want
        # to validate it, even when there are remaining lines that have
        # not yet been reserved.
        done = any(m.state == 'done' for m in self.move_lines) and \
            not any(move_line for move_line in
                    self.move_line_ids.filtered(lambda m: m.state != 'done'))
        if done:
            return False
        return no_reserved_quantities

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        if self.env.context.get('skip_backorder', False):
            return False
        return super(StockPicking, self)._create_backorder(
            backorder_moves=backorder_moves)
