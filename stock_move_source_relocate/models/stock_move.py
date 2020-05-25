# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        unconfirmed_moves = self.filtered(
            lambda m: m.state in ["confirmed", "partially_available"]
        )
        super()._action_assign()
        # could not be (entirely) reserved
        unconfirmed_moves = unconfirmed_moves.filtered(
            lambda m: m.state in ["confirmed", "partially_available"]
        )
        unconfirmed_moves._apply_source_relocate()

    def _apply_source_relocate(self):
        # Read the `reserved_availability` field of the moves out of the loop
        # to prevent unwanted cache invalidation when actually reserving.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        for move in self:
            # We don't need to ignore moves with "_should_bypass_reservation()
            # is True" because they are reserved at this point.
            relocation = self.env["stock.source.relocate"]._rule_for_move(move)
            if not relocation or relocation.relocate_location_id == move.location_id:
                continue
            move._apply_source_relocate_rule(
                relocation, reserved_availability, roundings
            )

    def _apply_source_relocate_rule(self, relocation, reserved_availability, roundings):
        relocated = self.env["stock.move"].browse()

        rounding = roundings[self]
        if not reserved_availability[self]:
            # nothing could be reserved, however, we want to source the
            # move on the specific relocation (for replenishment), so
            # update it's source location
            self.location_id = relocation.relocate_location_id
            relocated = self
        else:
            missing_reserved_uom_quantity = (
                self.product_uom_qty - reserved_availability[self]
            )
            need = self.product_uom._compute_quantity(
                missing_reserved_uom_quantity,
                self.product_id.uom_id,
                rounding_method="HALF-UP",
            )

            if float_is_zero(need, precision_rounding=rounding):
                return relocated

            # A part of the quantity could be reserved in the original
            # location, so keep this part in the move and split the rest
            # in a new move, where will take the goods in the relocation
            new_move_id = self._split(need)
            # recheck first move which should now be available
            new_move = self.browse(new_move_id)
            new_move.location_id = relocation.relocate_location_id
            self._action_assign()
            relocated = new_move
        return relocated
