# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _get_targeted_move_ids(self):
        moves = super()._get_targeted_move_ids()
        moves_to_remove = self.env["stock.move"]
        moves_to_add = self.env["stock.move"]
        for move in moves:
            mo = move.move_orig_ids.production_id[-1:]
            if mo and mo.picking_type_id.code == "mrp_operation":
                moves_to_remove |= move
                moves_to_add |= move.move_orig_ids
        return (moves - moves_to_remove) | moves_to_add
