# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_bypass_reservation(self, forced_location=False):
        return self.env.context.get(
            "force_bypass_reservation"
        ) or super()._should_bypass_reservation(forced_location=forced_location)

    def _action_assign(self, force_qty=False):
        # Do a first run to gather items in stock and then bypass the reservation for
        # the rest. FIXME: This won't work for items without tracking as the first
        # reserved line will be set to update with the whole move demand.
        res = super()._action_assign(force_qty=force_qty)
        moves_to_test_bypass = self.filtered(
            lambda x: x.picking_type_id and x.picking_type_id.bypass_reservation
        )
        if moves_to_test_bypass:
            moves_to_test_bypass.with_context(force_bypass_reservation=True)
            super(
                StockMove,
                moves_to_test_bypass.with_context(force_bypass_reservation=True),
            )._action_assign(force_qty=force_qty)
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        # Let's flag the bypassed move lines. It'll be handy to avoid issues when
        # unreserving.
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        if self.env.context.get("force_bypass_reservation"):
            vals.update({"bypassed_reservation": True})
        return vals
