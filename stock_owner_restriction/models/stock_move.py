# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_moves_to_assign_with_standard_behavior(self):
        """This method is expected to be extended as necessary. e.g. you may not want to
        handle subcontracting receipts (whose picking type is normal incoming receipt
        unless configured otherwise) with standard behavior, and you can filter out
        those moves.
        """
        return self.filtered(
            lambda m: not m.picking_type_id
            or m.picking_type_id.owner_restriction == "standard_behavior"
        )

    def _get_owner_for_assign(self):
        """This method is expected to be extended as necessary. e.g. different logic
        needs to be applied for moves in manufacturing orders.
        """
        self.ensure_one()
        partner = self.move_dest_ids.picking_id.owner_id
        if not partner:
            partner = self.picking_id.owner_id or self.picking_id.partner_id
        return partner

    def _action_assign(self, force_qty=False):
        # Split moves by picking type owner behavior restriction to process
        # moves depending of their owners
        moves = self._get_moves_to_assign_with_standard_behavior()
        res = super(StockMove, moves)._action_assign(force_qty=force_qty)
        dict_key = defaultdict(lambda: self.env["stock.move"])
        for move in self - moves:
            if move.picking_type_id.owner_restriction == "unassigned_owner":
                dict_key[False] |= move
            else:
                partner = move._get_owner_for_assign()
                dict_key[partner] |= move
        for owner_id, moves_to_assign in dict_key.items():
            super(
                StockMove,
                moves_to_assign.with_context(force_restricted_owner_id=owner_id),
            )._action_assign(force_qty=force_qty)
            if (
                owner_id
                and moves_to_assign.picking_type_id.owner_restriction
                == "partner_or_unassigned"
                and sum(
                    move.reserved_availability - move.product_uom_qty
                    for move in moves_to_assign
                )
                < 0
            ):
                super(
                    StockMove,
                    moves_to_assign.with_context(force_restricted_owner_id=False),
                )._action_assign(force_qty=force_qty)
        return res

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner_id is not None:
            owner_id = restricted_owner_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
