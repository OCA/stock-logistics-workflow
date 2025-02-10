# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    mto_as_mts = fields.Boolean()

    def _get_locations_for_mto_orderpoints(self):
        return self.mapped("lot_stock_id")

    def write(self, vals):
        res = super().write(vals)
        if "mto_as_mts" in vals and vals["mto_as_mts"] == False:
            self._archive_orderpoints_on_mts_mto_removal()
        return res

    def _archive_orderpoints_on_mts_mto_removal(self):
        for warehouse in self:
            domain = warehouse._get_orderpoints_to_archive_domain()
            orderpoints = self.env["stock.warehouse.orderpoint"].search(domain)
            if orderpoints:
                orderpoints.write({"active": False})

    def _get_orderpoints_to_archive_domain(self):
        self.ensure_one()
        locations = self._get_locations_for_mto_orderpoints()
        return [
            ("product_min_qty", "=", 0.0),
            ("product_max_qty", "=", 0.0),
            ("location_id", "in", locations.ids),
        ]
