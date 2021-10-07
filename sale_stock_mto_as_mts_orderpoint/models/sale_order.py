# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        res = super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
        self._run_orderpoints_for_mto_products()
        return res

    def _run_orderpoints_for_mto_products(self):
        orderpoints_to_procure_ids = []
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if not mto_route:
            return
        for line in self:
            delivery_move = line.move_ids.filtered(
                lambda m: m.picking_id.picking_type_code == "outgoing"
                and m.state not in ("done", "cancel")
            )
            if (
                not delivery_move.is_from_mto_route
                or mto_route not in line.product_id.route_ids
            ):
                continue
            orderpoint = line._get_mto_orderpoint()
            if orderpoint.procure_recommended_qty:
                orderpoints_to_procure_ids.append(orderpoint.id)
        wiz = (
            self.env["make.procurement.orderpoint"]
            .with_context(
                **{
                    "active_model": "stock.warehouse.orderpoint",
                    "active_ids": orderpoints_to_procure_ids,
                }
            )
            .create({})
        )
        wiz.make_procurement()

    def _get_mto_orderpoint(self):
        self.ensure_one()
        warehouse = self.warehouse_id or self.order_id.warehouse_id
        orderpoint = (
            self.env["stock.warehouse.orderpoint"]
            .with_context(active_test=False)
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    (
                        "location_id",
                        "=",
                        warehouse._get_locations_for_mto_orderpoints().id,
                    ),
                ],
                limit=1,
            )
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
                        "product_id": self.product_id.id,
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
