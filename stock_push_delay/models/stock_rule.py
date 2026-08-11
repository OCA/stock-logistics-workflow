# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    location_dest_from_rule = fields.Boolean(
        "Destination location origin from rule",
        default=True,
        help="When set to False the destination location of the stock.move "
        "will be the Operation Type one. Otherwise, it takes it from the rule.",
    )

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
        )
        if not self.location_dest_from_rule:
            res["location_dest_id"] = self.picking_type_id.default_location_dest_id.id
            res["location_final_id"] = location_dest_id.id
            res["route_ids"] = [self.route_id.id]
        return res

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if move_to_copy.product_qty != move_to_copy.quantity:
            res["product_uom_qty"] = move_to_copy.quantity
        return res
