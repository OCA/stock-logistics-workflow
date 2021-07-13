# Copyright 2021 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("lot_name")
    def onchange_lot_name(self):
        if self.lot_name:
            self.lot_id = self.env["stock.production.lot"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("name", "=", self.lot_name),
                ]
            )
        else:
            self.lot_id = False
