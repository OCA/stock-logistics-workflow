# Copyright 2014-2015 NDP Systèmes (<https://www.ndp-systemes.fr>)
# Copyright 2020 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
        res = super(StockMove, self)._action_assign()
        # Transfer all pickings which have an auto move assigned
        moves = self.filtered(lambda m: m.state == "assigned" and m.auto_move)
        moves._auto_assign_quantities()
        moves._action_done()
        already_assigned_moves = self.filtered(lambda m: m.state == "assigned")

        not_assigned_auto_move = self - already_assigned_moves

        # Process only moves that have been processed recently
        auto_moves = not_assigned_auto_move.filtered(
            lambda m: m.state in ("assigned", "partially_available") and m.auto_move
        )

        # group the moves by pickings
        auto_moves_by_pickings = self._get_auto_moves_by_pickings(auto_moves)

        # process the moves by creating backorders
        self.env["stock.picking"]._transfer_pickings_with_auto_move(
            auto_moves_by_pickings
        )
        return res

    @api.model
    def _get_auto_moves_by_pickings(self, auto_moves):
        """ Group moves by picking.
        @param auto_moves: stock.move data set
        @return dict dict of moves grouped by pickings
        {stock.picking(id): stock.move(id1, id2, id3 ...), ...}
        """
        auto_moves_by_pickings = dict()
        for move in auto_moves:
            if move.picking_id in auto_moves_by_pickings:
                auto_moves_by_pickings[move.picking_id] |= move
            else:
                auto_moves_by_pickings.update({move.picking_id: move})
        return auto_moves_by_pickings

    def _change_procurement_group(self):
        automatic_group = self.env.ref("stock_auto_move.automatic_group")
        moves = self.filtered(lambda m: m.auto_move and m.group_id != automatic_group)
        moves.write({"group_id": automatic_group.id})

    def _action_confirm(self, merge=True, merge_into=False):
        self._change_procurement_group()
        return super(StockMove, self)._action_confirm(
            merge=merge, merge_into=merge_into
        )
