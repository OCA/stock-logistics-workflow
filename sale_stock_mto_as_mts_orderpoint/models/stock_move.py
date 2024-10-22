# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    is_from_mto_route = fields.Boolean(compute="_compute_is_from_mto_route")

    def _compute_is_from_mto_route(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if not mto_route:
            self.update({"is_from_mto_route": False})
        else:
            for move in self:
                move.is_from_mto_route = move.rule_id.route_id == mto_route

    @api.model
    def _get_mto_orderpoint(self, warehouse, product):
        orderpoint_model = self.env["stock.warehouse.orderpoint"]
        orderpoint = orderpoint_model.with_context(active_test=False).search(
            [
                ("product_id", "=", product.id),
                (
                    "location_id",
                    "=",
                    warehouse._get_locations_for_mto_orderpoints().id,
                ),
            ],
            limit=1,
        )
        if orderpoint and not orderpoint.active:
            orderpoint.write(
                {"active": True, "product_min_qty": 0.0, "product_max_qty": 0.0}
            )
        elif not orderpoint:
            orderpoint = (
                self.env["stock.warehouse.orderpoint"]
                .sudo()
                .create(
                    {
                        "product_id": product.id,
                        "warehouse_id": warehouse.id,
                        "location_id": (
                            warehouse._get_locations_for_mto_orderpoints().id
                        ),
                        "product_min_qty": 0.0,
                        "product_max_qty": 0.0,
                    }
                )
            )
        return orderpoint

    def _get_mto_as_mts_orderpoints(self, warehouse):
        orderpoint_to_procure = self.env["stock.warehouse.orderpoint"]
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if not mto_route:
            return
        for move in self:
            if not (move.product_id._is_mto() or move.is_from_mto_route):
                continue
            orderpoint = move._get_mto_orderpoint(warehouse, move.product_id)
            if orderpoint.procure_recommended_qty:
                orderpoint_to_procure |= orderpoint
        return orderpoint_to_procure
