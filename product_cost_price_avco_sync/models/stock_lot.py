# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _get_avco_valued_totals(self, company):
        """Return the valued quantity and value of every lot in self, keyed by
        id. See `product.product._get_avco_valued_totals` for why the
        `quantity_svl` and `value_svl` fields can't be used here.
        """
        groups = (
            self.env["stock.valuation.layer"]
            .sudo()
            ._read_group(
                [("lot_id", "in", self.ids), ("company_id", "=", company.id)],
                ["lot_id"],
                ["quantity:sum", "value:sum"],
            )
        )
        totals = dict.fromkeys(self.ids, (0.0, 0.0))
        totals.update({lot.id: (qty, value) for lot, qty, value in groups})
        return totals

    def _get_avco_oversold_quantities(self, company):
        """Return the valued quantity of the lots in self that are sold below
        zero, restricted to products actually valuated by lot.
        """
        lots = self.filtered(
            lambda x: x.product_id.lot_valuated
            and x.product_id.with_company(company.id).cost_method == "average"
        )
        if not lots:
            return {}
        totals = lots._get_avco_valued_totals(company)
        return {
            lot.id: totals[lot.id][0]
            for lot in lots
            if float_compare(
                totals[lot.id][0],
                0.0,
                precision_rounding=lot.product_id.uom_id.rounding,
            )
            < 0
        }

    def write(self, vals):
        """Discard the cost core's negative stock vacuum computes for the lots
        that are still oversold when it finishes. See
        `product.product._run_fifo_vacuum`, which is what sets the flag.
        """
        keep_price_ids = self.env.context.get("avco_keep_price_lot_ids")
        if keep_price_ids and "standard_price" in vals:
            keep_price = self.filtered(lambda x: x.id in keep_price_ids)
            if keep_price:
                other_vals = {k: v for k, v in vals.items() if k != "standard_price"}
                res = True
                if other_vals:
                    res = super(StockLot, keep_price).write(other_vals)
                return super(StockLot, self - keep_price).write(vals) and res
        return super().write(vals)
