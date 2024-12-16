# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# Copyright 2018-2021 Jarsa Sistemas (Sarai Osorio <sarai.osorio@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiry_date = fields.Date()

    def _get_value_production_lot(self):
        vals = super()._get_value_production_lot()
        if self.product_id.use_expiry_date:
            vals["expiry_date"] = self.expiry_date
        return vals
