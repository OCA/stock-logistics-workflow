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
            move.quantity_done = move.product_qty

    def _action_assign(self):
        super(StockMove, self)._action_assign()
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(lambda m: m.state == "assigned" and m.auto_move)
        moves._auto_assign_quantities()
        moves._action_done()

    def _change_procurement_group(self):
        automatic_group = self.env.ref("stock_auto_move.automatic_group")
        moves = self.filtered(lambda m: m.auto_move and m.group_id != automatic_group)
        moves.write({"group_id": automatic_group.id})

    def _action_confirm(self, merge=True, merge_into=False):
        self._change_procurement_group()
        return super(StockMove, self)._action_confirm(
            merge=merge, merge_into=merge_into
        )
