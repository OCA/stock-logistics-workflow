# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        if self.rule_id.route_id:
            self = self.with_context(_putaway_route_id=self.rule_id.route_id)
        return super()._generate_serial_move_line_commands(
            lot_names, origin_move_line=origin_move_line
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        if self.rule_id.route_id:
            self = self.with_context(_putaway_route_id=self.rule_id.route_id)
        return super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
