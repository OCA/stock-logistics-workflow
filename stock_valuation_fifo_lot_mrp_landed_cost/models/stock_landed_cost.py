# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def button_validate(self):
        "Update Lots/SN on stock.valuation.layer line"
        res = super().button_validate()
        for rec in self.stock_valuation_layer_ids:
            lot_ids = self.mrp_production_ids.mapped("lot_producing_id")
            if lot_ids:
                rec.write({"lot_ids": lot_ids})
        return res
