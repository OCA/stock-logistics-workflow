# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models
from odoo.tools.float_utils import float_is_zero


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _button_validate_get_no_quantities_done(self):
        precision_digits = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        return all(
            float_is_zero(
                move_line.qty_done,
                precision_digits=precision_digits) for move_line in
            self.move_line_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')))

    def _validate_get_no_reserved_quantities(self):
        return all(
            float_is_zero(
                move_line.product_qty,
                precision_rounding=move_line.product_uom_id.rounding)
            for move_line in self.move_line_ids)
