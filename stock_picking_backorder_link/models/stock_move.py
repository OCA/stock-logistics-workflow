# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def propagate_move_dest_qty_reduction(self, qty=0):
        """ "
        This recursive method reduces the product_qty of the destination moves related
        to the stock.move in self. It will reduce in total the quantity established in
        the parameter qty. When a layer has been completed, it propagates the changes to
        the next layers.
        """
        self.ensure_one()
        if self.move_dest_ids and qty:
            to_cancel_qty = qty
            for move_dest in self.move_dest_ids.filtered(lambda m: m.state != "done"):
                if move_dest.product_uom_qty <= to_cancel_qty:
                    to_cancel_qty -= move_dest.product_qty
                    move_dest.propagate_move_dest_qty_reduction(
                        qty=move_dest.product_qty
                    )
                    move_dest._action_cancel()
                else:
                    move_dest.product_uom_qty -= to_cancel_qty
                    move_dest.propagate_move_dest_qty_reduction(qty=to_cancel_qty)
                    break
