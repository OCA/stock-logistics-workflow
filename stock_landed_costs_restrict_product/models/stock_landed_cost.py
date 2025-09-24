# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models, tools
from odoo.exceptions import ValidationError


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _check_can_validate(self):
        res = super()._check_can_validate()
        for landed_cost in self:
            if not landed_cost.valuation_adjustment_lines:
                raise ValidationError(
                    _("There are lines without valuation adjustments.")
                )
        return res

    def _get_totals(self, formula="cost_line_id:count"):
        read_domain = [("cost_id", "=", self.id)]
        read_groupby = ["cost_line_id"]
        totals = {
            cost_line_id.id: total_qty
            for cost_line_id, total_qty in self.env[
                "stock.valuation.adjustment.lines"
            ]._read_group(
                domain=read_domain,
                groupby=read_groupby,
                aggregates=[formula],
            )
        }
        return totals

    def _update_cost_valuation_adjustment_lines(self, towrite_dict):
        for key, value in towrite_dict.items():
            line_id = self.env["stock.valuation.adjustment.lines"].browse(key)
            line_id.write({"additional_landed_cost": value})

    def compute_landed_cost(self):
        res = super().compute_landed_cost()
        apply_rule = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_landed_costs_product.landed_costs_apply_rule")
        )
        if apply_rule:
            towrite_dict = {}
            for landed_cost in self.filtered(
                lambda landed_cost: landed_cost._get_targeted_move_ids()
            ):
                landed_cost = landed_cost.with_company(landed_cost.company_id)
                for valuation in landed_cost.valuation_adjustment_lines:
                    if not valuation._check_rule():
                        valuation.unlink()
                totals_line = landed_cost._get_totals()
                totals_qty = landed_cost._get_totals("quantity:sum")
                totals_weight = landed_cost._get_totals("weight:sum")
                totals_volume = landed_cost._get_totals("volume:sum")
                totals_cost = landed_cost._get_totals("former_cost:sum")
                rounding = landed_cost.currency_id.rounding
                for line in landed_cost.cost_lines:
                    value_split = 0.0
                    for valuation in landed_cost.valuation_adjustment_lines:
                        if (
                            valuation.cost_line_id
                            and valuation.cost_line_id.id == line.id
                        ):
                            if line.split_method == "by_quantity" and totals_qty.get(
                                line.id, 0
                            ):
                                per_unit = line.price_unit / totals_qty.get(line.id, 0)
                                value = valuation.quantity * per_unit
                            elif line.split_method == "by_weight" and totals_weight.get(
                                line.id, 0
                            ):
                                per_unit = line.price_unit / totals_weight.get(
                                    line.id, 0
                                )
                                value = valuation.weight * per_unit
                            elif line.split_method == "by_volume" and totals_volume.get(
                                line.id, 0
                            ):
                                per_unit = line.price_unit / totals_volume.get(
                                    line.id, 0
                                )
                                value = valuation.volume * per_unit
                            elif line.split_method == "equal":
                                value = line.price_unit / totals_line.get(line.id, 0)
                            elif (
                                line.split_method == "by_current_cost_price"
                                and totals_cost.get(line.id, 0)
                            ):
                                per_unit = line.price_unit / totals_cost.get(line.id, 0)
                                value = valuation.former_cost * per_unit
                            else:
                                value = line.price_unit / totals_line.get(line.id, 0)
                            if rounding:
                                value = tools.float_round(
                                    value,
                                    precision_rounding=rounding,
                                    rounding_method="HALF-UP",
                                )
                                value_split += value
                            if valuation.id not in towrite_dict:
                                towrite_dict[valuation.id] = value
                            else:
                                towrite_dict[valuation.id] += value
                    rounding_diff = landed_cost.currency_id.round(
                        line.price_unit - value_split
                    )
                    if not landed_cost.currency_id.is_zero(rounding_diff):
                        towrite_dict[max(towrite_dict.keys())] += rounding_diff
                landed_cost._update_cost_valuation_adjustment_lines(towrite_dict)
        return res
