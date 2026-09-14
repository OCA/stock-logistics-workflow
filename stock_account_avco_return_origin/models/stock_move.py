# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_avco_origin_return(self):
        self.ensure_one()
        origin_move = self.origin_returned_move_id
        return bool(
            self.company_id.avco_return_origin_cost
            and origin_move
            and origin_move._is_in()
            and origin_move.location_id.usage == "supplier"
            and self.with_company(self.company_id).product_id.cost_method == "average"
        )

    def _sync_avco_origin_standard_price(self, product, company):
        product = product.with_company(company)
        product.invalidate_recordset(["value_svl", "quantity_svl"])
        if (
            float_compare(
                product.quantity_svl, 0, precision_rounding=product.uom_id.rounding
            )
            <= 0
        ):
            # Stock depleted (or negative): the emptying/over return was valued at
            # standard AVCO (see product._prepare_out_svl_vals), so there is no
            # residual to realign.
            return
        product.sudo().with_context(disable_auto_svl=True).standard_price = (
            product.value_svl / product.quantity_svl
        )

    def _create_out_svl(self, forced_quantity=None):
        origin_returns = self.filtered(lambda m: m._is_avco_origin_return())
        normal = self - origin_returns
        # When a single _action_done() batch mixes normal out moves with origin
        # returns of the same product, the normal moves are intentionally valued
        # first, at the average in effect before any return realignment, and the
        # standard_price is realigned only once at the end (below). A batch has no
        # defined move order, and core AVCO already values all batched out moves
        # at the same pre-batch average; the return correction applies going
        # forward, not retroactively to same-batch deliveries. Do not reorder.
        layers = super(StockMove, normal)._create_out_svl(
            forced_quantity=forced_quantity
        )
        for move in origin_returns:
            layers |= super(
                StockMove, move.with_context(avco_origin_return_move_id=move.id)
            )._create_out_svl(forced_quantity=forced_quantity)
            # Realign after each move so that a later return in the same batch
            # sees an average reflecting the value already removed by earlier
            # origin returns. Deferring this would let a return whose quantity
            # empties stock fall back to a stale average and strand valuation
            # (qty 0 with value != 0).
            move._sync_avco_origin_standard_price(move.product_id, move.company_id)
        return layers
