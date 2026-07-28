# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_avco_valued_totals(self, company):
        """Return the valued quantity and value of every product in self, keyed
        by id.

        The `quantity_svl` and `value_svl` fields can't be used for this. They
        are computed with `@api.depends("stock_valuation_layer_ids")`, which
        doesn't catch a quantity or value change on an already existing layer,
        which is exactly what this module does all the time, so reading them
        would leave a stale value in cache for the rest of the transaction.
        """
        groups = (
            self.env["stock.valuation.layer"]
            .sudo()
            ._read_group(
                [("product_id", "in", self.ids), ("company_id", "=", company.id)],
                ["product_id"],
                ["quantity:sum", "value:sum"],
            )
        )
        totals = dict.fromkeys(self.ids, (0.0, 0.0))
        totals.update({product.id: (qty, value) for product, qty, value in groups})
        return totals

    def _get_avco_oversold_quantities(self, company):
        """Return the valued quantity of the average cost products in self that
        are sold below zero, keyed by id.
        """
        products = self.with_company(company.id).filtered(
            lambda x: x.cost_method == "average"
        )
        totals = products._get_avco_valued_totals(company)
        return {
            product.id: totals[product.id][0]
            for product in products
            if float_compare(
                totals[product.id][0],
                0.0,
                precision_rounding=product.uom_id.rounding,
            )
            < 0
        }

    def _set_avco_standard_price_from_layers(self, company):
        """Derive the product cost from its own layers.

        This is what a product valuated by lot needs: the cost that drives the
        outgoing moves is the lot's one, and the product's is only a summary of
        what is in stock. Core derives it the very same way, in
        `stock_lot._change_standard_price` and in `account_move._post` of
        `purchase_stock`. Products with no stock left, or oversold ones, are
        skipped: dividing by that quantity means nothing, and with a negative
        one it would flip the sign of the cost.
        """
        totals = self._get_avco_valued_totals(company)
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for product in self:
            quantity, value = totals[product.id]
            if (
                float_compare(quantity, 0.0, precision_rounding=product.uom_id.rounding)
                <= 0
            ):
                continue
            new_price = float_round(value / quantity, precision_digits=precision)
            target = product.with_company(company.id)
            if float_compare(
                target.standard_price, new_price, precision_digits=precision
            ):
                target.with_context(
                    disable_auto_svl=True
                ).sudo().standard_price = new_price

    def _run_fifo_vacuum(self, company=None):
        """Keep the cost price of every product and lot the vacuum settles.

        Core closes the vacuum writing `standard_price = value_svl /
        quantity_svl`, both for the product and for each lot of a product
        valuated by lot, guarded only against a zero quantity. Two things are
        wrong with that division here:

        1. When the receipt that triggered the vacuum isn't enough to cover the
           whole deficit, the denominator is negative and the cost flips sign.
        2. Even when it is enough, the numerator now carries the layers the
           vacuum has just written, which have **no quantity**: they settle
           units that already left the company, so they say nothing about what
           the stock still on hand is worth. Seen in production on 7303NCORTE,
           a production order left it at 6,6567 EUR/unit and the vacuum
           immediately rewrote it to 8,3811, which is `1141,67 / 136,220` after
           three `Revaluation of ... (negative inventory)` layers had added
           210,41 EUR settling 52,18 units delivered a month and a half
           earlier. The 136,22 units on hand got 26% more expensive because of
           goods that are no longer there.

        This is the same rule `stock.valuation.layer._is_avco_spreadable_value`
        applies when replaying a chain, so both paths agree on the cost, which
        is the invariant this module keeps. The price that stands is the one
        `stock.move.product_price_update_before_done` derived from the real
        incoming cost, and it is the only one written along the whole
        validation.

        Whatever the settlement leaves unabsorbed shows up as the gap between
        `value_svl` and `quantity_svl * standard_price`: a visible, fixable
        discrepancy rather than a cost nobody can trace back to a purchase.
        """
        company = company or self.env.company
        keep_lot_ids = []
        lot_valuated = self.filtered("lot_valuated")
        if lot_valuated:
            # sudo: the vacuum runs on validation, by whoever validates, and a
            # user with no inventory rights can't read the lots
            keep_lot_ids = (
                self.env["stock.lot"]
                .sudo()
                .search([("product_id", "in", lot_valuated.ids)])
                .ids
            )
        products = self.with_context(
            avco_keep_price_product_ids=self.ids,
            avco_keep_price_lot_ids=keep_lot_ids,
        )
        return super(ProductProduct, products)._run_fifo_vacuum(company=company)

    def write(self, vals):
        keep_price_ids = self.env.context.get("avco_keep_price_product_ids")
        if keep_price_ids and "standard_price" in vals:
            keep_price = self.filtered(lambda x: x.id in keep_price_ids)
            if keep_price:
                other_vals = {k: v for k, v in vals.items() if k != "standard_price"}
                res = True
                if other_vals:
                    res = super(ProductProduct, keep_price).write(other_vals)
                return super(ProductProduct, self - keep_price).write(vals) and res
        return super().write(vals)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        """Enabling or disabling the valuation by lot moves every product to a
        different set of valuation chains, so the layers core writes to empty
        the stock out and put it back must not trigger a resync in between.
        """
        if "lot_valuated" in vals:
            self = self.with_context(skip_avco_sync=True)
        return super().write(vals)
