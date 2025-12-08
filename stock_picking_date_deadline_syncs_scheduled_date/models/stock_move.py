# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        if values.get("date_deadline"):
            values.update({"date": values["date_deadline"]})
        return super().write(values)
