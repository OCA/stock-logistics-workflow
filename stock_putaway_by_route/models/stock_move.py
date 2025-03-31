# Copyright 2020 Camptocamp
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        if self.rule_id.route_id:
            self = self.with_context(_putaway_route_id=self.rule_id.route_id)
        elif self.product_id.route_ids:
            self = self.with_context(_putaway_route_id=self.product_id.route_ids)
        return super()._generate_serial_move_line_commands(
            lot_names, origin_move_line=origin_move_line
        )

    def _get_putaway_routes(self):
        routes = self.env["stock.location.route"]
        if self.rule_id.route_id:
            routes = self.rule_id.route_id
        elif self.product_id.route_ids:
            routes = self.product_id.route_ids
        return routes

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        putaway_routes = self._get_putaway_routes()
        if putaway_routes:
            self = self.with_context(_putaway_route_id=putaway_routes)
        return super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
