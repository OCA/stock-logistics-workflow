# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = [_name, "product.cost.price.avco.sync.mixin"]

    _avco_layer_link_field = "lot_id"
    _avco_keep_price_context_key = "avco_keep_price_lot_ids"

    def _avco_oversold_candidates(self, company):
        """Restrict the check to products actually valuated by lot."""
        return self.filtered(
            lambda x: x.product_id.lot_valuated
            and x.product_id.with_company(company.id).cost_method == "average"
        )

    def _avco_uom_rounding(self):
        self.ensure_one()
        return self.product_id.uom_id.rounding
