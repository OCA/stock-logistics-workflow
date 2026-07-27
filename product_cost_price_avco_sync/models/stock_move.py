# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def product_price_update_before_done(self, forced_qty=None):
        """Don't let a receipt validated on negative stock wreck the cost price.

        Core weights the incoming cost against the accumulated quantity even
        when that quantity is negative, and dividing by a negative denominator
        returns a price that is not an average of anything: a receipt at a
        higher cost can lower the average or even turn it negative, and every
        outgoing layer created afterwards copies that broken cost.

        Oversold products take their cost from `_get_avco_svl_price` instead,
        which sets the incoming cost as the new average.
        """
        # Lot valued products are left to core, as their cost has to be
        # computed for each lot separately.
        incoming = self.filtered(lambda x: x._is_in() and not x.product_id.lot_valuated)
        oversold_quantities = {
            company.id: moves.product_id._get_avco_oversold_quantities(company)
            for company, moves in incoming.grouped("company_id").items()
        }
        svl_model = self.env["stock.valuation.layer"]
        avco_prices = {}
        for move in incoming:
            previous_qty = oversold_quantities[move.company_id.id].get(
                move.product_id.id
            )
            if previous_qty is None:
                continue
            product = move.product_id.with_company(move.company_id)
            quantity = (
                forced_qty[1]
                if forced_qty
                else sum(move._get_in_move_lines().mapped("quantity_product_uom"))
            )
            # Several moves of the same product can be validated at once. Their
            # layers aren't created until after this method, so the quantity
            # stays negative for all of them and the last cost is the one that
            # prevails.
            key = (move.company_id.id, product.id)
            avco_prices[key] = svl_model._get_avco_svl_price(
                avco_prices.get(key, product.standard_price),
                previous_qty,
                next(iter(move._get_price_unit().values())),
                quantity,
            )
        res = super().product_price_update_before_done(forced_qty=forced_qty)
        for (company_id, product_id), new_price in avco_prices.items():
            self.env["product.product"].browse(product_id).with_company(
                company_id
            ).with_context(disable_auto_svl=True).sudo().standard_price = new_price
        return res
