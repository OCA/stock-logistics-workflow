# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class ProductCostPriceAvcoSyncMixin(models.AbstractModel):
    """Shared behaviour of `product.product` and `stock.lot` as the two kinds
    of records a `stock.valuation.layer` can be valued against: reading their
    valued quantity/value straight from the layers, spotting the oversold
    ones, and keeping a cost the negative stock vacuum wrote out of a record
    the module has flagged to preserve.
    """

    _name = "product.cost.price.avco.sync.mixin"
    _description = "Product Cost Price AVCO Sync Mixin"

    # Field of `stock.valuation.layer` that links a layer to a record of this
    # model ("product_id" or "lot_id"). Set by each concrete model.
    _avco_layer_link_field = ""
    # Context key carrying the ids whose `standard_price` write must be
    # discarded (see `write` below). Set by each concrete model.
    _avco_keep_price_context_key = ""

    def _get_avco_valued_totals(self, company):
        """Return the valued quantity and value of every record in self,
        keyed by id.

        The `quantity_svl`/`value_svl` fields can't be used for this. They
        are computed with `@api.depends("stock_valuation_layer_ids")`, which
        doesn't catch a quantity or value change on an already existing
        layer, which is exactly what this module does all the time, so
        reading them would leave a stale value in cache for the rest of the
        transaction.
        """
        groups = (
            self.env["stock.valuation.layer"]
            .sudo()
            ._read_group(
                [
                    (self._avco_layer_link_field, "in", self.ids),
                    ("company_id", "=", company.id),
                ],
                [self._avco_layer_link_field],
                ["quantity:sum", "value:sum"],
            )
        )
        totals = dict.fromkeys(self.ids, (0.0, 0.0))
        totals.update({record.id: (qty, value) for record, qty, value in groups})
        return totals

    def _avco_oversold_candidates(self, company):
        """Records in self eligible for the oversold check: valuated by
        average cost. Overridden by `stock.lot`, which also requires the
        product to be valuated by lot.
        """
        return self.with_company(company.id).filtered(
            lambda x: x.cost_method == "average"
        )

    def _avco_uom_rounding(self):
        """Rounding of the UoM the quantity is expressed in."""
        self.ensure_one()
        return self.uom_id.rounding

    def _get_avco_oversold_quantities(self, company):
        """Return the valued quantity of the records in self that are sold
        below zero, keyed by id.
        """
        candidates = self._avco_oversold_candidates(company)
        if not candidates:
            return {}
        totals = candidates._get_avco_valued_totals(company)
        return {
            record.id: totals[record.id][0]
            for record in candidates
            if float_compare(
                totals[record.id][0],
                0.0,
                precision_rounding=record._avco_uom_rounding(),
            )
            < 0
        }

    def write(self, vals):
        """Discard the cost core's negative stock vacuum computes for the
        records still flagged to keep their price. See
        `product.product._run_fifo_vacuum`, which sets the flag.
        """
        keep_price_ids = self.env.context.get(self._avco_keep_price_context_key)
        if keep_price_ids and "standard_price" in vals:
            keep_price = self.filtered(lambda x: x.id in keep_price_ids)
            if keep_price:
                other_vals = {k: v for k, v in vals.items() if k != "standard_price"}
                res = True
                if other_vals:
                    res = super(ProductCostPriceAvcoSyncMixin, keep_price).write(
                        other_vals
                    )
                return (
                    super(ProductCostPriceAvcoSyncMixin, self - keep_price).write(vals)
                    and res
                )
        return super().write(vals)
