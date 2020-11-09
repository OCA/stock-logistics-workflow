# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        # Split moves by picking type owner behavior restriction to process
        # moves depending of their owners
        moves = self.filtered(
            lambda m: m.picking_type_id.owner_restriction == "standard_behavior"
        )
        super(StockMove, moves)._action_assign()
        dict_key = defaultdict(lambda: self.env["stock.move"])
        for move in self - moves:
            if move.picking_type_id.owner_restriction == "unassigned_owner":
                dict_key[False] |= move
            else:
                dict_key[move.picking_id.owner_id or move.picking_id.partner_id] |= move
        for owner_id, moves_to_assign in dict_key.items():
            super(
                StockMove,
                moves_to_assign.with_context(force_restricted_owner_id=owner_id),
            )._action_assign()

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
