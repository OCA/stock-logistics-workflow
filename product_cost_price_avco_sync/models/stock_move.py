# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_avco_quantities_by_lot(self, forced_qty=None):
        """Return the incoming quantity of the move keyed by lot, mirroring what
        core does in `product_price_update_before_done`. A product that isn't
        valuated by lot gets a single entry under an empty lot.
        """
        self.ensure_one()
        if forced_qty:
            return {forced_qty[0]: forced_qty[1]}
        quantities = defaultdict(float)
        for line in self._get_in_move_lines():
            lot = line.lot_id if self.product_id.lot_valuated else self.env["stock.lot"]
            quantities[lot] += line.quantity_product_uom
        return quantities

    def product_price_update_before_done(self, forced_qty=None):
        """Don't let a receipt validated on negative stock wreck the cost price.

        Core weights the incoming cost against the accumulated quantity even
        when that quantity is negative, and dividing by a negative denominator
        returns a price that is not an average of anything: a receipt at a
        higher cost can lower the average or even turn it negative, and every
        outgoing layer created afterwards copies that broken cost. It repeats
        the very same computation per lot for the products valuated by lot,
        with the very same missing guard.

        Whoever is oversold, product or lot, takes its cost from
        `_get_avco_svl_price` instead, which sets the incoming cost as the new
        average.
        """
        incoming = self.filtered(lambda x: x._is_in())
        oversold_products = {}
        oversold_lots = {}
        for company, moves in incoming.grouped("company_id").items():
            oversold_products[company.id] = (
                moves.product_id._get_avco_oversold_quantities(company)
            )
            oversold_lots[company.id] = moves.lot_ids._get_avco_oversold_quantities(
                company
            )
        svl_model = self.env["stock.valuation.layer"]
        prices = {}
        for move in incoming:
            product = move.product_id.with_company(move.company_id)
            costs = move._get_price_unit()
            quantities = move._get_avco_quantities_by_lot(forced_qty)
            targets = []
            # The product cost is guarded in every case: core blends it even
            # for the products valuated by lot, and only derives it afterwards
            # when the stock is positive.
            product_qty = oversold_products[move.company_id.id].get(product.id)
            if product_qty is not None:
                # The whole move feeds the product chain, at the cost of its
                # last lot, which is the one that prevails under this rule
                last_lot = list(quantities)[-1]
                targets.append(
                    (
                        product,
                        product_qty,
                        costs[last_lot],
                        sum(quantities.values()),
                    )
                )
            if product.lot_valuated:
                for lot, quantity in quantities.items():
                    lot_qty = oversold_lots[move.company_id.id].get(lot.id)
                    if lot_qty is not None:
                        targets.append(
                            (
                                lot.with_company(move.company_id),
                                lot_qty,
                                costs[lot],
                                quantity,
                            )
                        )
            for target, previous_qty, cost, quantity in targets:
                # Several moves of the same product or lot can be validated at
                # once. Their layers aren't created until after this method, so
                # the quantity stays negative for all of them and the last cost
                # is the one that prevails.
                prices[target] = svl_model._get_avco_svl_price(
                    prices.get(target, target.standard_price),
                    previous_qty,
                    cost,
                    quantity,
                )
        res = super().product_price_update_before_done(forced_qty=forced_qty)
        for target, new_price in prices.items():
            target.with_context(disable_auto_svl=True).sudo().standard_price = new_price
        return res

    def _product_price_update_after_done(self):
        """Core derives the product cost of a lot valuated product from its own
        layers after an outgoing move, `value_svl / quantity_svl`, guarded only
        against a zero quantity. Dividing a negative value by a negative
        quantity gives a positive number that means nothing, so an oversold
        product keeps the cost taken from its real incoming price.
        """
        skipped = self.env["stock.move"]
        for company, moves in self.grouped("company_id").items():
            oversold = moves.product_id._get_avco_oversold_quantities(company)
            skipped |= moves.filtered(lambda x: x.product_id.id in oversold)  # noqa: B023
        return super(StockMove, self - skipped)._product_price_update_after_done()
