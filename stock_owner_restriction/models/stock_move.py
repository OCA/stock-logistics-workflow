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
        res = True
        moves = self._get_moves_to_assign_with_standard_behavior()
        if moves:
            res = super(StockMove, moves)._action_assign(force_qty=force_qty)

        # Group remaining moves by owner ID or False
        dict_key = defaultdict(lambda: self.env["stock.move"])
        for move in self - moves:
            if move.picking_type_id.owner_restriction == "unassigned_owner":
                owner_key = False
                dict_key[owner_key] |= move
            else:
                partner = move._get_owner_for_assign()
                owner_key = partner.id if partner else False
                dict_key[owner_key] |= move

        # Process grouped moves
        for owner_id_key, moves_to_assign in dict_key.items():
            ctx = {"force_restricted_owner_id": owner_id_key}
            super(
                StockMove,
                moves_to_assign.with_context(**ctx),
            )._action_assign(force_qty=force_qty)

            # --- Logic for partner_or_unassigned ---
            # Check if owner_id_key is a valid partner ID (not False)
            if (
                owner_id_key is not False
                and moves_to_assign
                # Check restriction type on the first move
                # (assuming all in group are same)
                and moves_to_assign[0].picking_type_id.owner_restriction
                == "partner_or_unassigned"
                and sum(
                    move.quantity - move.product_uom_qty for move in moves_to_assign
                )
                < 0
            ):
                ctx_unassigned = {"force_restricted_owner_id": False}
                super(
                    StockMove,
                    moves_to_assign.with_context(**ctx_unassigned),
                )._action_assign(force_qty=force_qty)
        return res

    def _update_reserved_quantity(
        self,
        need,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        restricted_owner_id_ctx = self.env.context.get(
            "force_restricted_owner_id", None
        )

        owner_arg_for_super = owner_id

        # If the calling method didn't specify an owner
        # AND there's a restriction in context
        if owner_arg_for_super is None and restricted_owner_id_ctx is not None:
            if isinstance(restricted_owner_id_ctx, int):
                # Convert the ID from context back to a recordset
                owner_recordset = self.env["res.partner"].browse(
                    restricted_owner_id_ctx
                )
                # Use False if ID was invalid, otherwise the recordset
                owner_arg_for_super = (
                    owner_recordset if owner_recordset.exists() else False
                )
            elif restricted_owner_id_ctx is False:
                owner_arg_for_super = False

        return super()._update_reserved_quantity(
            need,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_arg_for_super,
            strict=strict,
        )
