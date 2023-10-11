# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def _update_stock_move(self):
        """Remove code done on mrp_subcontracting_account as is done in future versions.
        That's done because this method is linking the same move on different svls.
        Not needed for v14+.
        """
        return True

    def _preprocess_rest_svl_to_sync(self, svls_dic, preprocess_svl_dic):
        if (
            self.stock_move_id.production_id
            and self.stock_move_id.move_dest_ids[:1].is_subcontract
        ):
            # We have to propagate the change on the subcontracting value to the
            # production to keep the change for possible future changes
            production = self.stock_move_id.production_id
            price_extra_cost = self.stock_move_id.move_dest_ids[0]._get_price_unit()
            if production.extra_cost != price_extra_cost:
                production.extra_cost = price_extra_cost
        return super()._preprocess_rest_svl_to_sync(svls_dic, preprocess_svl_dic)
