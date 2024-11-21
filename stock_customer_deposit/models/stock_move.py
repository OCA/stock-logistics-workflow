# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        if self.env.context.get("owner", False):
            return super(StockMove, self)._action_assign(force_qty=force_qty)

        # Warehouse not configured to use customer deposits
        no_deposit_config_moves = self.filtered(
            lambda move: not move.warehouse_id.use_customer_deposits
        )
        super(StockMove, no_deposit_config_moves)._action_assign(force_qty=force_qty)
        # Warehouse configured to use customer deposits
        deposit_config_moves = self - no_deposit_config_moves
        # Move needs to create deposit
        moves_push_deposit_route = deposit_config_moves.filtered(
            lambda move: move.warehouse_id.customer_deposit_route_id in move.route_ids
        )
        # Move needs to take from deposit or stock
        moves_pull_from_stock = deposit_config_moves - moves_push_deposit_route
        for move in moves_pull_from_stock:
            # Check if move can take from deposit
            move_owner_qty = move._get_available_quantity(
                move.location_id,
                lot_id=None,
                package_id=None,
                owner_id=move.partner_id.commercial_partner_id or move.partner_id,
                strict=False,
                allow_negative=False,
            )
            owner = False
            if (
                float_compare(
                    move_owner_qty,
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding,
                )
                >= 0
            ):
                # Enough qty to take from deposit: Propagate assign with owner context
                owner = move.partner_id.commercial_partner_id.id or move.partner_id.id
            super(StockMove, move.with_context(owner=owner))._action_assign(
                force_qty=force_qty
            )

        return super(
            StockMove, moves_push_deposit_route.with_context(owner=False)
        )._action_assign(force_qty=force_qty)

    def _get_out_move_lines(self):
        """Also consider as "out" move lines to those that belongs to
        a picking type that assigns owners
        and are in a location that should be valued."""
        res = super()._get_out_move_lines()
        for move in self.filtered(lambda m: m.picking_type_id.assign_owner):
            res |= move.move_line_ids.filtered(
                lambda ml: ml.location_id._should_be_valued()
            )
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        res = super()._apply_putaway_strategy()
        for ml in self.filtered(lambda ml: ml.move_id.picking_type_id.assign_owner):
            ml.location_dest_id = ml.location_id
        return res
