# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    def _get_locations_for_mto_orderpoints(self):
        return self.mapped("lot_stock_id")
