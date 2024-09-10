# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import groupby


class StockMove(models.Model):
    _inherit = "stock.move"

    def all_moves_can_be_bought(self):
        for move in self:
            if not move.product_id.purchase_ok:
                return False
        return True

    def _get_mto_as_mts_orderpoints(self, warehouse):
        orderpoints_to_procure = self.env["stock.warehouse.orderpoint"]

        if self.all_moves_can_be_bought():
            return super()._get_mto_as_mts_orderpoints(warehouse)

        seen_moves = self.browse()
        for bom, bom_move_list in groupby(self, key=lambda m: m.bom_line_id.bom_id):
            bom_moves = self.browse([move.id for move in bom_move_list])
            if not bom or not bom_moves:
                # In case a move doesn't have a bom, do nothing
                continue

            bom_product = bom.product_id
            bom_lines = bom.bom_line_ids
            move_bom_lines = bom_moves.bom_line_id
            if bom_lines != move_bom_lines:
                continue

            is_mto = bom_product._is_mto() or all(bom_moves.is_from_mto_route)
            if not bom_moves.all_moves_can_be_bought() and is_mto:
                orderpoint = self._get_mto_orderpoint(warehouse, bom_product)
                if orderpoint.procure_recommended_qty:
                    orderpoints_to_procure |= orderpoint
                # All bom_moves has been handled
                seen_moves |= bom_moves

        remaining_moves = self - seen_moves
        return (
            super(StockMove, remaining_moves)._get_mto_as_mts_orderpoints(warehouse)
            | orderpoints_to_procure
        )
