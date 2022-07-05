# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="stock_valuation_layer_id",
        string="Valuation Usage",
        help="Trace on what stock moves has the stock valuation been used in, "
        "including the quantities taken.",
    )
    incoming_usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="dest_stock_valuation_layer_id",
        string="Incoming Valuation Usage",
        help="Trace on what stock moves has the stock valuation been used in, "
        "including the quantities taken.",
    )

    incoming_usage_quantity = fields.Float(
        string="Incoming Usage quantity",
        compute="_compute_incoming_usages",
        store=True,
    )
    incoming_usage_value = fields.Float(
        string="Incoming Usage value", compute="_compute_incoming_usages", store=True,
    )

    @api.depends(
        "incoming_usage_ids.quantity", "incoming_usage_ids.value",
    )
    def _compute_incoming_usages(self):
        for rec in self:
            rec.incoming_usage_quantity = sum(rec.incoming_usage_ids.mapped("quantity"))
            rec.incoming_usage_value = sum(rec.incoming_usage_ids.mapped("value"))

    usage_quantity = fields.Float(
        string="Usage quantity", compute="_compute_usage_values", store=True,
    )
    usage_value = fields.Float(
        string="Usage value", compute="_compute_usage_values", store=True,
    )

    @api.depends(
        "usage_ids.quantity", "usage_ids.value",
    )
    def _compute_usage_values(self):
        for rec in self:
            rec.usage_quantity = sum(rec.usage_ids.mapped("quantity"))
            rec.usage_value = sum(rec.usage_ids.mapped("value"))

    def _process_taken_data(self, taken_data, rec):
        usage_model = self.env["stock.valuation.layer.usage"]
        for origin_layer_id in taken_data.keys():
            usage_model.create(
                {
                    "stock_valuation_layer_id": origin_layer_id,
                    "dest_stock_valuation_layer_id": rec.id,
                    "stock_move_id": rec.stock_move_id.id,
                    "quantity": taken_data.get(origin_layer_id).get("quantity", 0.0),
                    "value": taken_data.get(origin_layer_id).get("value", 0.0),
                    "company_id": rec.company_id.id,
                }
            )
        return True

    @api.model_create_multi
    def create(self, values):
        recs = self.browse()
        for val in values:
            taken_data = "taken_data" in val.keys() and val.pop("taken_data") or {}
            rec = super(StockValuationLayer, self).create(val)
            # There are cases in which the transformation
            # comes from a return process,
            # such as sales returns or production unbuilds.
            # To maintain traceability,
            # the initial output layers are added as origin.
            if not taken_data and rec.quantity > 0:
                all_parents = self.env["stock.move"]
                next_parents = rec.stock_move_id.move_orig_ids.filtered(
                    lambda m: m not in all_parents
                )
                while next_parents:
                    all_parents |= next_parents
                    next_parents = next_parents.mapped("move_orig_ids").filtered(
                        lambda m: m not in all_parents
                    )
                if all_parents:
                    output_layers = self.search(
                        [
                            ("stock_move_id", "in", all_parents.ids),
                            ("quantity", "<", 0),
                        ],
                        order="create_date",
                    )
                    qty_to_take_on_candidates = rec.quantity
                    for candidate in output_layers:
                        qty_taken_on_candidate = min(
                            qty_to_take_on_candidates, abs(candidate.quantity)
                        )
                        taken_data[candidate.id] = {"quantity": qty_taken_on_candidate}
                        candidate_unit_cost = abs(candidate.value) / abs(
                            candidate.quantity
                        )
                        value_taken_on_candidate = (
                            qty_taken_on_candidate * candidate_unit_cost
                        )
                        value_taken_on_candidate = candidate.currency_id.round(
                            value_taken_on_candidate
                        )
                        taken_data[candidate.id].update(
                            {"value": value_taken_on_candidate}
                        )
                        qty_to_take_on_candidates -= qty_taken_on_candidate
                        if float_is_zero(
                            qty_to_take_on_candidates,
                            precision_rounding=rec.uom_id.rounding,
                        ):
                            break
            self._process_taken_data(taken_data, rec)
            recs |= rec
        return recs

    def write(self, values):
        res = super(StockValuationLayer, self).write(values)
        for rec in self:
            if self.env.context.get("taken_data"):
                self._process_taken_data(self.env.context.get("taken_data"), rec)
        return res
