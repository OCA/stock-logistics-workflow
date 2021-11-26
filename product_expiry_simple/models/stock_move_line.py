# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# Copyright 2018-2021 Jarsa Sistemas (Sarai Osorio <sarai.osorio@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiry_date = fields.Date(string="Expiry Date")

    # When you read the code of _create_and_assign_production_lot()
    # you need the defects of that method:
    # 1. it's not possible to inherit the creation of the lot
    # 2. it creates one lot per company/product/lot_name
    # On that second point, we can consider that, for a particular product,
    # lot X will always have the same expiry_date

    def _assign_production_lot(self, lot):
        super()._assign_production_lot(lot)
        if self[0].expiry_date:
            self.lot_id.write({"expiry_date": self[0].expiry_date})
