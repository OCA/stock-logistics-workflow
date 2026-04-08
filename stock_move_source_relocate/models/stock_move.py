# Copyright 2020 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        unconfirmed_moves = self.filtered(
            lambda m: m.state in ["confirmed", "partially_available"]
        )
        result = super()._action_assign(force_qty=force_qty)
        # could not be (entirely) reserved
        unconfirmed_moves = unconfirmed_moves.filtered(
            lambda m: m.state in ["confirmed", "partially_available"]
        )
        if unconfirmed_moves:
            unconfirmed_moves._apply_source_relocate()
        return result

    def _apply_source_relocate(self):
        """Apply relocation rules.

        Returns the recordset of confirmed and partially available moves
        """
        # Read the `quantity` field of the moves out of the loop
        # to prevent unwanted cache invalidation when actually reserving.
        quantity = {move: move.quantity for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        relocated_ids = []
        _logger.debug(
            f"Try to relocate moves of operation type ("
            f"{', '.join(self.picking_type_id.mapped('name'))})"
        )
        res_ids = []
        for move in self:
            # We don't need to ignore moves with "_should_bypass_reservation()
            # is True" because they are reserved at this point.
            relocation = self.env["stock.source.relocate"]._rule_for_move(move)
            if not relocation or relocation.relocate_location_id == move.location_id:
                res_ids.append(move.id)
                continue
            relocated = move._apply_source_relocate_rule(
                relocation, quantity, roundings
            )
            if relocated:
                relocated_ids.append(relocated.id)
                res_ids.append(relocated.id)
            else:
                res_ids.append(move.id)
        if relocated_ids:
            _logger.debug(f"Relocated moves {relocated_ids}")
            self.browse(relocated_ids)._after_apply_source_relocate_rule()
        return self.browse(res_ids)

    def _apply_source_relocate_rule(self, relocation, quantity, roundings):
        self.ensure_one()
        rounding = roundings[self]
        qty_reserved = quantity[self]
        if float_compare(qty_reserved, 0, precision_rounding=rounding) == 0:
            # nothing could be reserved, however, we want to source the
            # move on the specific relocation (for replenishment), so
            # update it's source location
            self.location_id = relocation.relocate_location_id
            # Do not call _action_confirm on a split moves inside _action_assign
            return self

        missing_reserved_uom_quantity = self.product_uom_qty - qty_reserved
        need = self.product_uom._compute_quantity(
            missing_reserved_uom_quantity,
            self.product_id.uom_id,
            rounding_method="HALF-UP",
        )
        if float_compare(need, 0, precision_rounding=rounding) <= 0:
            return self.env["stock.move"].browse()

        # A part of the quantity could be reserved in the original
        # location, so keep this part in the move and split the rest
        # in a new move, where will take the goods in the relocation
        move_vals_list = self._split(need)
        for move_vals in move_vals_list:
            move_vals["location_id"] = relocation.relocate_location_id.id
            # Do not call _action_confirm on a split moves inside _action_assign
            move_vals["state"] = "confirmed"
            move_vals["reservation_date"] = self.reservation_date
        return self.create(move_vals_list)

    def _after_apply_source_relocate_rule(self, merge=True):
        if merge:
            _logger.debug("Try to merge relocated moves")
            # When the unassigned move is relocated in the same picking as the
            # assigned move, merge back the assigned move into the relocated
            # moves. Ensure the current move does not disappear as we are
            # inside _action_assign
            for moves in self.grouped("picking_id").values():
                (moves.picking_id.move_ids - moves)._merge_moves(merge_into=moves)
