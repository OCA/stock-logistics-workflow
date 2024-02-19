# Copyright 2023 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model
    def _cal_price_mrp(self, quantity, svls_dic):
        """Get the cost price for the production order linked to this SVL.
        NOTE: This is adaptation of the method _cal_price in mrp_account.
        """
        finished_move = self.stock_move_id
        production = finished_move.production_id
        cost = 0
        for cons_move in finished_move.move_line_ids.consume_line_ids.move_id:
            svl = cons_move.stock_valuation_layer_ids[:1]
            cost -= svls_dic.get(svl, {"value": svl.value})["value"]
        work_center_cost = 0
        for work_order in production.workorder_ids:
            time_lines = work_order.time_ids.filtered(
                lambda x: x.date_end and not x.cost_already_recorded
            )
            duration = sum(time_lines.mapped("duration"))
            work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
        svl = finished_move.stock_valuation_layer_ids[:1]
        currency = svl.currency_id
        qty_done = finished_move.product_uom._compute_quantity(
            quantity, finished_move.product_id.uom_id
        )
        extra_cost = production.extra_cost * qty_done
        return currency.round((cost + work_center_cost + extra_cost) / qty_done)

    def _postprocess_rest_svl_to_sync(self, svls_dic, postprocess_svl_dic):
        """If this SVL is the consumption of a raw material, we should affect the cost
        of the finished products for such production order.
        """
        if self.stock_move_id.raw_material_production_id:
            production = self.stock_move_id.raw_material_production_id
            for move in production.move_finished_ids.filtered(
                lambda x: x.state == "done"
                and x.quantity_done > 0
                and x.product_id.cost_method == "average"
            ):
                svl = move.stock_valuation_layer_ids[:1]
                unit_cost = svl._cal_price_mrp(svl.quantity, svls_dic)
                postprocess_svl_dic[svl] = {
                    "unit_cost": unit_cost,
                    "value": unit_cost * svl.quantity,
                }
                return True
        return super()._postprocess_rest_svl_to_sync(svls_dic, postprocess_svl_dic)

    def _preprocess_rest_svl_to_sync(self, svls_dic, preprocess_svl_dic):
        """If this SVL is coming from a move of a production order, we get the unit cost
        from the consumed materials, not doing anything more with it.
        """
        if self.stock_move_id.production_id:
            svl_dic = svls_dic[self]
            svl_dic["unit_cost"] = self._cal_price_mrp(svl_dic["quantity"], svls_dic)
            return True
        return super()._preprocess_rest_svl_to_sync(svls_dic, preprocess_svl_dic)
