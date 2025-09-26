# Copyright 2014-2015 NDP Systèmes (<https://www.ndp-systemes.fr>)
# Copyright 2020 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the move will be automatically "
        "processed as soon as the products are available.",
    )

    def _auto_assign_quantities(self):
        for move in self:
            move.picked = True

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty=force_qty)
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(
            lambda m: m.state in ("assigned", "partially_available") and m.auto_move
        )
        if moves:
            moves._auto_assign_quantities()
            # In case of no backorder on the first move and cancel propagation
            # we need to propagate cancel_backorder to action_done
            moves._action_done(
                cancel_backorder=self.env.context.get("cancel_backorder", False)
            )
            # We need to create backorder if there are mixed moves (auto and manual)
            moves.mapped("picking_id")._create_backorder()
        return res

    def _change_procurement_group(self):
        automatic_group = self.env.ref("stock_auto_move.automatic_group")
        moves = self.filtered(lambda m: m.auto_move and not m.group_id)
        moves.write({"group_id": automatic_group.id})

    def _action_confirm(self, merge=True, merge_into=False):
        self._change_procurement_group()
        return super()._action_confirm(merge=merge, merge_into=merge_into)
