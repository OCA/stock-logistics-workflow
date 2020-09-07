# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, vals):
        """ Update cost price avco """
        if "price_unit" not in vals:
            return super().write(vals)
        incoming_moves = self.env['stock.move'].browse()
        for line in self:
            incoming_moves |= line._get_outgoing_incoming_moves()[1].filtered(
                lambda m: m.state == 'done')
        for move in incoming_moves:
            self.env['stock.move.line']._create_correction_svl(move, -move.quantity_done)
        res = super().write(vals)
        for move in incoming_moves:
            self.env['stock.move.line']._create_correction_svl(move, move.quantity_done)
        return res
