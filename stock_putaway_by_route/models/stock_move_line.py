# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("product_id", "product_uom_id")
    def onchange_product_id(self):
        if self.product_id.route_ids:
            self = self.with_context(_putaway_route_id=self.product_id.route_ids)
        return super().onchange_product_id()
