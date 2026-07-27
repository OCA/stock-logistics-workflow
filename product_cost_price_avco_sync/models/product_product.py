# Copyright 2024 Tecnativa - Pedro M. Baeza
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_avco_valued_quantities(self, company):
        """Return the valued quantity of every product in self, keyed by id.

        The `quantity_svl` field can't be used for this. It is computed with
        `@api.depends("stock_valuation_layer_ids")`, which doesn't catch a
        quantity or value change on an already existing layer, which is exactly
        what this module does all the time, so reading it would leave a stale
        value in cache for the rest of the transaction.
        """
        groups = (
            self.env["stock.valuation.layer"]
            .sudo()
            ._read_group(
                [("product_id", "in", self.ids), ("company_id", "=", company.id)],
                ["product_id"],
                ["quantity:sum"],
            )
        )
        quantities = dict.fromkeys(self.ids, 0.0)
        quantities.update({product.id: quantity for product, quantity in groups})
        return quantities

    def _get_avco_oversold_quantities(self, company):
        """Return the valued quantity of the average cost products in self that
        are sold below zero, keyed by id.
        """
        products = self.with_company(company.id).filtered(
            lambda x: x.cost_method == "average"
        )
        quantities = products._get_avco_valued_quantities(company)
        return {
            product.id: quantities[product.id]
            for product in products
            if float_compare(
                quantities[product.id],
                0.0,
                precision_rounding=product.uom_id.rounding,
            )
            < 0
        }

    def _run_fifo_vacuum(self, company=None):
        """Keep the cost price of the products that are still oversold.

        Core closes the vacuum writing `standard_price = value_svl /
        quantity_svl`, guarded only against a zero quantity. When the receipt
        that triggered the vacuum isn't enough to cover the whole deficit, that
        division has a negative denominator and flips the sign of the cost.

        Flagging those products makes `write` discard that final value, so the
        cost taken from the real incoming price in
        `stock.move.product_price_update_before_done` is the only one written
        along the whole validation.
        """
        company = company or self.env.company
        # The vacuum only creates layers with no quantity, so the products that
        # are oversold now are the very same ones that will still be oversold
        # when it finishes.
        oversold_ids = list(self._get_avco_oversold_quantities(company))
        products = self
        if oversold_ids:
            products = self.with_context(avco_keep_price_product_ids=oversold_ids)
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
