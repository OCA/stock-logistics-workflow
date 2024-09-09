# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    mto_as_mts = fields.Boolean(inverse="_inverse_mto_as_mts")

    def _get_locations_for_mto_orderpoints(self):
        return self.mapped("lot_stock_id")

    def _inverse_mto_as_mts(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if not mto_route:
            return
        for warehouse in self:
            if warehouse.mto_as_mts:
                wh_mto_rules = self.env["stock.rule"].search(
                    [
                        ("route_id", "=", mto_route.id),
                        "|",
                        ("warehouse_id", "=", warehouse.id),
                        ("picking_type_id.warehouse_id", "=", warehouse.id),
                    ]
                )
                if wh_mto_rules:
                    wh_mto_rules.active = False
