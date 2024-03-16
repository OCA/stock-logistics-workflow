# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.fields import first


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _get_value_production_lot(self):
        res = super()._get_value_production_lot()
        if "name" in res and not res["name"]:
            del res["name"]
        return res

    def set_lot_auto(self):
        """
        Create lots using create_multi to avoid too much queries
        As move lines were created by product or by tracked 'serial'
        products, we apply the lot with both different approaches.
        """
        values = []
        stock_lot_obj = self.env["stock.lot"]
        lots_by_product = dict()
        for line in self:
            # Prepare multi valued lots per line to use multi creation.
            values.append(line._get_value_production_lot())
        lots = stock_lot_obj.create(values)
        for lot in lots:
            if lot.product_id.id not in lots_by_product:
                lots_by_product[lot.product_id.id] = lot
            else:
                lots_by_product[lot.product_id.id] += lot
        for line in self:
            lot = first(lots_by_product[line.product_id.id])
            line.lot_id = lot
            if lot.product_id.tracking == "serial":
                lots_by_product[line.product_id.id] -= lot
