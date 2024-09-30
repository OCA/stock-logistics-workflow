# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.tools import groupby


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        res = super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
        self._run_orderpoints_for_mto_products()
        return res

    @api.model
    def _get_procurement_wiz_for_orderpoint_ids(self, context):
        model = self.env["make.procurement.orderpoint"]
        return model.with_context(**context).create({})

    def _run_orderpoints_for_mto_products(self):
        orderpoints_to_procure = self.env["stock.warehouse.orderpoint"]
        lines_per_warehouse = groupby(
            self, key=lambda l: l.warehouse_id or l.order_id.warehouse_id
        )
        for warehouse, line_list in lines_per_warehouse:
            lines = self.browse([line.id for line in line_list])
            delivery_moves = lines.move_ids.filtered(
                lambda m: m.picking_id.picking_type_code == "outgoing"
                and m.state not in ("done", "cancel")
            )
            if warehouse.mto_as_mts:
                orderpoints_to_procure |= delivery_moves._get_mto_as_mts_orderpoints(
                    warehouse
                )
        context = {
            "active_model": "stock.warehouse.orderpoint",
            "active_ids": orderpoints_to_procure.ids,
        }
        wiz = self._get_procurement_wiz_for_orderpoint_ids(context)
        wiz.make_procurement()

    def _get_mto_orderpoint(self, product_id):
        self.ensure_one()
        warehouse = self.warehouse_id or self.order_id.warehouse_id
        orderpoint = (
            self.env["stock.warehouse.orderpoint"]
            .with_context(active_test=False)
            .search(
                [
                    ("product_id", "=", product_id.id),
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
                        "product_id": product_id.id,
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
