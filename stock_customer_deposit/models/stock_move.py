# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        if self.env.context.get("owner", False):
            return super(StockMove, self)._action_assign(force_qty=force_qty)
        # moves from warehouse with customer deposits activate
        moves_customer_deposits = self.filtered(
            lambda move: move.warehouse_id.use_customer_deposits
        )
        # moves with warehouse that have deactivated customer deposits should not do anything.
        super(StockMove, self - moves_customer_deposits)._action_assign(
            force_qty=force_qty
        )
        # moves with warehouse that have activated customer deposits must assign owner
        moves_owner = moves_customer_deposits.filtered(
            lambda m: self.env["stock.quant"]._get_available_quantity(
                m.product_id,
                m.location_id,
                owner_id=m.partner_id.commercial_partner_id or m.partner_id,
            )
            > 0.0
        )
        for move in moves_owner:
            super(
                StockMove,
                move.with_context(
                    owner=move.partner_id.commercial_partner_id.id or move.partner_id.id
                ),
            )._action_assign(force_qty=force_qty)
        return super(
            StockMove, (moves_customer_deposits - moves_owner).with_context(owner=False)
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
