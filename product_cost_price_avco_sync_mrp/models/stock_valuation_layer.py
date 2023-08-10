# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model
    def _cal_price_mrp(self, production, finished_move, consumed_values_list, svls_dic):
        work_center_cost = 0
        for work_order in production.workorder_ids:
            time_lines = work_order.time_ids.filtered(
                lambda x: x.date_end and not x.cost_already_recorded
            )
            duration = sum(time_lines.mapped("duration"))
            time_lines.write({"cost_already_recorded": True})
            work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
        svl = finished_move.stock_valuation_layer_ids[:1]
        currency = svl.currency_id
        qty = (
            svls_dic[svl]["quantity"]
            if svl in svls_dic
            else finished_move.quantity_done
        )
        qty_done = finished_move.product_uom._compute_quantity(
            qty, finished_move.product_id.uom_id
        )
        extra_cost = production.extra_cost * qty_done
        return {
            "unit_cost": currency.round(
                (sum(consumed_values_list) + work_center_cost + extra_cost) / qty_done
            )
        }

    @api.model
    def _get_consumed_values(self, finished_move, svls_dic):
        consumed_values_list = []
        cosumed_moves = finished_move.move_line_ids.consume_line_ids.move_id
        for cons_move in cosumed_moves:
            if cons_move.stock_valuation_layer_ids[:1] in svls_dic:
                consumed_values_list.append(
                    abs(svls_dic[cons_move.stock_valuation_layer_ids[:1]]["value"])
                )
            else:
                consumed_values_list.append(
                    abs(cons_move.stock_valuation_layer_ids[:1]["value"])
                )
        return consumed_values_list

    def _postprocess_rest_svl_to_sync(self, svls_dic, postprocess_svl_dic):
        if self.stock_move_id.raw_material_production_id:
            production = self.stock_move_id.raw_material_production_id
            for move in production.move_finished_ids.filtered(
                lambda x: x.state == "done"
                and x.quantity_done > 0
                and x.product_id.cost_method == "average"
            ):
                svl = move.stock_valuation_layer_ids[:1]
                consumed_values_list = self._get_consumed_values(move, svls_dic)
                dict_price = self._cal_price_mrp(
                    production, move, consumed_values_list, svls_dic
                )
                qty = svls_dic[svl]["quantity"] if svl in svls_dic else svl.quantity
                dict_price["value"] = dict_price["unit_cost"] * qty
                postprocess_svl_dic[svl] = dict_price
        return super()._postprocess_rest_svl_to_sync(svls_dic, postprocess_svl_dic)

    def _preprocess_rest_svl_to_sync(self, svls_dic, preprocess_svl_dic):
        if self.stock_move_id.production_id:
            production = self.stock_move_id.production_id
            svl = self.stock_move_id.stock_valuation_layer_ids[:1]
            consumed_values_list = self._get_consumed_values(
                self.stock_move_id, svls_dic
            )
            svls_dic[svl].update(
                self._cal_price_mrp(
                    production, self.stock_move_id, consumed_values_list, svls_dic
                )
            )
            return True
        return super()._preprocess_rest_svl_to_sync(svls_dic, preprocess_svl_dic)
