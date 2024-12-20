# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        """Override to set the location_id of negative return moves to the default
        location_dest_id of the return picking type."""
        neg_r_moves = self.filtered(
            lambda move: float_compare(
                move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding
            )
            < 0
        )
        self = self.with_context(neg_r_moves=neg_r_moves.ids)
        return super()._action_confirm(merge=merge, merge_into=merge_into)

    def set_negative_return_moves_location(self):
        """Set the location_id of negative return moves to the default location_dest_id
        of the return picking type."""
        neg_r_moves = self.browse(self.env.context["neg_r_moves"])
        for move in neg_r_moves:
            if move.picking_type_id.return_picking_type_id.default_location_dest_id:
                move.location_id = (
                    move.picking_type_id.return_picking_type_id.default_location_dest_id
                )

    def _check_company(self, fnames=None):
        # Set the location_id of negative return moves to the default location_dest_id
        # of the return picking type
        # We hook into this method used in stock.move._action_confirm
        # (see https://github.com/odoo/odoo/blob/
        # 3a63c90fff615b70881131e11d7375af2ae082a6/addons/stock/models/stock_move.py
        # #L1381C14-L1381C27)
        # to be able to invert location_id and location_dest_id
        if self.env.context.get("neg_r_moves"):
            self.set_negative_return_moves_location()
        return super()._check_company(fnames=fnames)
