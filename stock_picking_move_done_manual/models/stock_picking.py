# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.float_utils import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

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

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        if self.env.context.get('skip_backorder', False):
            return False
        return super(StockPicking, self)._create_backorder(
            backorder_moves=backorder_moves)
