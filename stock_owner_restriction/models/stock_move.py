# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")
    restricted_owner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_restricted_owner_id",
    )

    @api.depends(
        "move_dest_ids.picking_id.owner_id",
        "picking_id.owner_id",
        "picking_id.partner_id",
    )
    def _compute_restricted_owner_id(self):
        for move in self:
            move.restricted_owner_id = move._get_owner_for_assign()[:1]

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
                    move.quantity - move.product_uom_qty for move in moves_to_assign
                )
                < 0
            ):
                super(
                    StockMove,
                    moves_to_assign.with_context(force_restricted_owner_id=False),
                )._action_assign(force_qty=force_qty)
        return res

    def _update_reserved_quantity_vals(
        self,
        need,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        # Overridden instead of _update_reserved_quantity because the chained
        # moves path in _action_assign calls this method directly.
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner_id is not None:
            owner_id = restricted_owner_id
        return super()._update_reserved_quantity_vals(
            need,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _set_quantity_done(self, qty):
        # stock.move.quantity's inverse: reserves quants directly, bypassing
        # _action_assign entirely (manual immediate quantities, MRP
        # consumption, subcontracting, or any import writing this field).
        self.ensure_one()
        if (
            not self.picking_type_id
            or self.picking_type_id.owner_restriction == "standard_behavior"
        ):
            return super()._set_quantity_done(qty)
        owner_id = (
            False
            if self.picking_type_id.owner_restriction == "unassigned_owner"
            else self._get_owner_for_assign()
        )
        res = super(
            StockMove, self.with_context(force_restricted_owner_id=owner_id)
        )._set_quantity_done(qty)
        if (
            owner_id
            and self.picking_type_id.owner_restriction == "partner_or_unassigned"
            and float_compare(
                self.quantity, qty, precision_rounding=self.product_uom.rounding
            )
            < 0
        ):
            res = super(
                StockMove, self.with_context(force_restricted_owner_id=False)
            )._set_quantity_done(qty)
        return res
