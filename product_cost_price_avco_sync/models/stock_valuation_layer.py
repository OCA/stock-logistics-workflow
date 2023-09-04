# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from collections import OrderedDict, defaultdict

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_vacuum(self, company=None):
        if self.cost_method != "average":
            return super()._run_fifo_vacuum()


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

    @api.model
    def create(self, vals):
        svl = super().create(vals)
        if vals.get("quantity", 0.0) > 0.0 and svl.product_id.cost_method == "average":
            svl_remaining = self.sudo().search(
                [
                    ("company_id", "=", svl.company_id.id),
                    ("product_id", "=", svl.product_id.id),
                    ("remaining_qty", "<", 0.0),
                ],
                order="id",
                limit=1,
            )
            if svl_remaining:
                svl.cost_price_avco_sync({}, {})
        return svl

    def write(self, vals):
        """Update cost price avco"""
        svl_previous_vals = defaultdict(dict)
        if ("unit_cost" in vals or "quantity" in vals) and not self.env.context.get(
            "skip_avco_sync"
        ):
            for svl in self:
                for field_name in set(vals.keys()) & {"unit_cost", "quantity"}:
                    svl_previous_vals[svl.id][field_name] = svl[field_name]
        res = super().write(vals)
        if svl_previous_vals:
            self.cost_price_avco_sync(vals, svl_previous_vals)
        return res

    def get_svls_to_avco_sync(self):
        self.ensure_one()
        # return self.product_id.stock_valuation_layer_ids
        domain = [
            ("company_id", "=", self.company_id.id),
            ("product_id", "=", self.product_id.id),
        ]
        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id")
        )

    def get_avco_svl_qty_unit_cost(self, line, vals):
        self.ensure_one()
        if self.id == line.id:
            qty = vals.get("quantity", line.quantity)
            unit_cost = vals.get("unit_cost", line.unit_cost)
        else:
            qty = self.quantity
            unit_cost = self.unit_cost
        return qty, unit_cost

    @api.model
    def process_avco_svl_inventory(
        self, svl, svl_dic, line, svl_previous_vals, previous_unit_cost
    ):
        high_decimal_precision = 8
        new_svl_qty = svl_dic["quantity"] + (
            svl_previous_vals[line.id]["quantity"] - line.quantity
        )
        # Check if with the new difference the sign of the move changes
        if (new_svl_qty < 0 and svl.stock_move_id.location_id.usage == "inventory") or (
            new_svl_qty > 0 and svl.stock_move_id.location_dest_id.usage == "inventory"
        ):
            location_aux = svl.stock_move_id.location_id
            svl.stock_move_id.location_id = svl.stock_move_id.location_dest_id
            svl.stock_move_id.location_dest_id = location_aux
            svl.stock_move_id.move_line_ids.location_id = svl.stock_move_id.location_id
            svl.stock_move_id.move_line_ids.location_dest_id = (
                svl.stock_move_id.location_dest_id
            )
        # TODO: Split new_svl_qty in related stock move lines
        if (
            float_compare(
                abs(new_svl_qty),
                svl.stock_move_id.quantity_done,
                precision_digits=high_decimal_precision,
            )
            != 0
        ):
            if len(svl.stock_move_id.move_line_ids) > 1:
                raise ValidationError(
                    _(
                        "More than one stock move line to assign the new "
                        "stock valuation layer quantity"
                    )
                )
            svl.stock_move_id.quantity_done = abs(new_svl_qty)
        # Reasign qty variables
        qty = new_svl_qty
        svl_dic["quantity"] = new_svl_qty
        svl_dic["unit_cost"] = previous_unit_cost
        svl_dic["value"] = svl_dic["quantity"] * previous_unit_cost
        if new_svl_qty > 0:
            svl_dic["remaining_qty"] = new_svl_qty
        else:
            svl_dic["remaining_qty"] = 0.0
        svl_dic["remaining_value"] = svl_dic["unit_cost"] * svl_dic["remaining_qty"]
        return qty

    @api.model
    def update_avco_svl_values(self, svl_dic, unit_cost=None, remaining_qty=None):
        if unit_cost is not None:
            svl_dic["unit_cost"] = unit_cost
        svl_dic["value"] = svl_dic["unit_cost"] * svl_dic["quantity"]
        if remaining_qty is not None:
            svl_dic["remaining_qty"] = remaining_qty
        svl_dic["remaining_value"] = svl_dic["remaining_qty"] * svl_dic["unit_cost"]

    @api.model
    def get_avco_svl_price(
        self, previous_unit_cost, previous_qty, unit_cost, qty, total_qty
    ):
        return (
            (previous_unit_cost * previous_qty + unit_cost * qty) / total_qty
            if total_qty
            else unit_cost
        )

    def vacumm_avco_svl(self, qty, svls_dic, vacuum_dic):
        self.ensure_one()
        svl_dic = svls_dic[self]
        vacuum_qty = qty
        for svl_to_vacuum in filter(
            lambda ln: ln["remaining_qty"] < 0 and ln["quantity"] < 0.0,
            svls_dic.values(),
        ):
            if abs(svl_to_vacuum["remaining_qty"]) <= vacuum_qty:
                vacuum_qty = vacuum_qty + svl_to_vacuum["remaining_qty"]
                diff_qty = -svl_to_vacuum["remaining_qty"]
                new_remaining_qty = 0.0
            else:
                new_remaining_qty = svl_to_vacuum["remaining_qty"] + vacuum_qty
                diff_qty = vacuum_qty
                vacuum_qty = 0.0
            vacuum_dic[svl_to_vacuum["id"]].append(
                (diff_qty, svls_dic[self]["unit_cost"])
            )
            x = 0.0
            for q, c in vacuum_dic[svl_to_vacuum["id"]]:
                x += q * c
            if new_remaining_qty:
                x += abs(new_remaining_qty) * vacuum_dic[svl_to_vacuum["id"]][0][1]
            new_unit_cost = x / abs(svl_to_vacuum["quantity"])
            # Update remaining in outgoing line
            self.update_avco_svl_values(
                svl_to_vacuum, unit_cost=new_unit_cost, remaining_qty=new_remaining_qty
            )
            # Update remaining in incoming line
            self.update_avco_svl_values(svl_dic, remaining_qty=vacuum_qty)
            if vacuum_qty == 0.0:
                break

    def update_remaining_avco_svl_in(self, svls_dic, vacuum_dic):
        for svl in self:
            svl_dic = svls_dic[svl]
            svl_out_qty = svl_dic["quantity"]
            for svl_in_remaining in filter(
                lambda ln: ln["remaining_qty"] > 0, svls_dic.values()
            ):
                if abs(svl_out_qty) <= svl_in_remaining["remaining_qty"]:
                    new_remaining_qty = svl_in_remaining["remaining_qty"] + svl_out_qty
                    vacuum_dic[svl.id].append((svl_out_qty, svl_dic["unit_cost"]))
                    svl_out_qty = 0.0
                else:
                    svl_out_qty = svl_out_qty + svl_in_remaining["remaining_qty"]
                    vacuum_dic[svl.id].append(
                        (svl_in_remaining["remaining_qty"], svl_dic["unit_cost"])
                    )
                    new_remaining_qty = 0.0
                self.update_avco_svl_values(
                    svl_in_remaining, remaining_qty=new_remaining_qty
                )
                if svl_out_qty == 0.0:
                    break
            self.update_avco_svl_values(svl_dic, remaining_qty=svl_out_qty)

    @api.model
    def process_avco_svl_manual_adjustements(self, svls_dic):
        accumulated_qty = accumulated_value = 0.0
        for svl, svl_dic in svls_dic.items():
            if (
                not svl_dic["quantity"]
                and not svl_dic["unit_cost"]
                and not svl.stock_move_id
                and svl.description
            ):
                match_price = re.findall(r"[+-]?[0-9]+\.[0-9]+\)$", svl.description)
                if match_price:
                    standard_price = float(match_price[0][:-1])
                    svl_dic["value"] = (
                        standard_price * accumulated_qty
                    ) - accumulated_value
            accumulated_qty = accumulated_qty + svl_dic["quantity"]
            accumulated_value = accumulated_value + svl_dic["value"]

    @api.model
    def update_avco_svl_modified(self, svls_dic, skip_avco_sync=True):
        for svl, svl_dic in svls_dic.items():
            vals = {}
            for field_name, new_value in svl_dic.items():
                if field_name == "id":
                    continue
                # Currency decimal precision for values and high precision to others
                elif field_name in ("unit_cost", "value", "remaining_value"):
                    prec_digits = svl.currency_id.decimal_places
                else:
                    prec_digits = 8
                if svl[field_name] != 0.0 and float_is_zero(
                    new_value, precision_digits=prec_digits
                ):
                    vals[field_name] = 0.0
                elif float_compare(
                    svl[field_name],
                    new_value,
                    precision_digits=prec_digits,
                ):
                    vals[field_name] = new_value
            # Write modified fields
            if vals:
                svl.with_context(skip_avco_sync=skip_avco_sync).write(vals)

    def _preprocess_main_svl_line(self):
        """This method serves for doing any stuff before processing the SVL, and it
        also allows to skip the line returning True.
        """
        return False

    def _preprocess_rest_svl_to_sync(self, svls_dic, preprocess_svl_dic):
        """This method serves for doing any stuff before processing subsequent SVLs that
        are being synced, and it also allows to skip the line returning True.
        """
        return False

    def cost_price_avco_sync(self, vals, svl_previous_vals):  # noqa: C901
        dp_obj = self.env["decimal.precision"]
        precision_qty = dp_obj.precision_get("Product Unit of Measure")
        precision_price = dp_obj.precision_get("Product Price")
        for line in self.sorted(key=lambda l: (l.create_date, l.id)):
            bypass = line._preprocess_main_svl_line()
            if (
                line.product_id.cost_method != "average"
                or line.stock_valuation_layer_id
                or bypass
            ):
                continue
            previous_unit_cost = previous_qty = 0.0
            svls_to_avco_sync = line.with_context(
                skip_avco_sync=True
            ).get_svls_to_avco_sync()
            vacuum_dic = defaultdict(list)
            inventory_processed = False
            unit_cost_processed = False
            svls_dic = OrderedDict()
            # SVLS that need to be written in a previous process before processing
            # the other SVLS.
            preprocess_svl_dic = OrderedDict()
            for svl in svls_to_avco_sync:
                if svl._preprocess_rest_svl_to_sync(svls_dic, preprocess_svl_dic):
                    continue
                # Compatibility with landed cost
                if svl.stock_valuation_layer_id:
                    linked_layer = svl.stock_valuation_layer_id
                    cost_to_add = svl.value
                    if cost_to_add and previous_qty:
                        previous_unit_cost += cost_to_add / previous_qty
                        svls_dic[linked_layer]["remaining_value"] += cost_to_add
                    continue
                qty, unit_cost = svl.get_avco_svl_qty_unit_cost(line, vals)
                svls_dic[svl] = {
                    "id": svl.id,
                    "quantity": qty,
                    "unit_cost": unit_cost,
                    "remaining_qty": qty,
                    "remaining_value": qty * unit_cost,
                    "value": svl.value,
                }
                svl_dic = svls_dic[svl]
                f_compare = float_compare(qty, 0.0, precision_digits=precision_qty)
                # Keep inventory unit_cost if not previous incoming or manual adjustment
                if not unit_cost_processed:
                    previous_unit_cost = unit_cost
                    if f_compare > 0.0:
                        unit_cost_processed = True
                # Adjust inventory IN and OUT
                # Discard moves with a picking because they are not an inventory
                if (
                    (
                        svl.stock_move_id.location_id.usage == "inventory"
                        or svl.stock_move_id.location_dest_id.usage == "inventory"
                    )
                    and not svl.stock_move_id.picking_id
                    and not svl.stock_move_id.scrapped
                ):
                    if (
                        not inventory_processed
                        # Context to keep stock quantities after inventory qty update
                        and self.env.context.get("keep_avco_inventory", False)
                    ):
                        qty = self.process_avco_svl_inventory(
                            svl,
                            svl_dic,
                            line,
                            svl_previous_vals,
                            previous_unit_cost,
                        )
                        inventory_processed = True
                    else:
                        svl.update_avco_svl_values(
                            svl_dic, unit_cost=previous_unit_cost
                        )
                    # Check if adjust IN and we have moves to vacuum outs without stock
                    if svl_dic["quantity"] > 0.0 and previous_qty < 0.0:
                        svl.vacumm_avco_svl(qty, svls_dic, vacuum_dic)
                    elif svl_dic["quantity"] < 0.0:
                        svl.update_remaining_avco_svl_in(svls_dic, vacuum_dic)
                    previous_qty = previous_qty + qty
                # Incoming line in layer
                elif f_compare > 0:
                    total_qty = previous_qty + qty
                    # Return moves
                    if not svl.stock_move_id or svl.stock_move_id.move_orig_ids:
                        svl.update_avco_svl_values(
                            svl_dic, unit_cost=previous_unit_cost
                        )
                    # Normal incoming moves
                    else:
                        unit_cost_processed = True
                        if previous_qty <= 0.0:
                            # Set income svl.unit_cost as previous_unit_cost
                            previous_unit_cost = unit_cost
                        else:
                            previous_unit_cost = svl.get_avco_svl_price(
                                previous_unit_cost,
                                previous_qty,
                                unit_cost,
                                qty,
                                total_qty,
                            )
                    svl.update_avco_svl_values(svl_dic, remaining_qty=qty)
                    if previous_qty < 0:
                        # Vacuum previous product outs without stock
                        svl.vacumm_avco_svl(qty, svls_dic, vacuum_dic)
                    previous_qty = total_qty
                # Outgoing line in layer
                elif f_compare < 0:
                    # Normal OUT
                    svl.update_avco_svl_values(
                        svl_dic,
                        unit_cost=previous_unit_cost,
                    )
                    previous_qty = previous_qty + qty
                    svl.update_remaining_avco_svl_in(svls_dic, vacuum_dic)
                # Manual standard_price adjustment line in layer
                elif (
                    not unit_cost
                    and not qty
                    and not svl.stock_move_id
                    and svl.description
                ):
                    unit_cost_processed = True
                    match_price = re.findall(r"[+-]?[0-9]+\.[0-9]+\)$", svl.description)
                    if match_price:
                        standard_price = float(match_price[0][:-1])
                        # TODO: Review abs in previous_qty or new_diff
                        new_diff = standard_price - previous_unit_cost
                        svl_dic["value"] = new_diff * previous_qty
                        previous_unit_cost = standard_price
                    # elif previous_qty > 0.0:
                    #     previous_unit_cost = (
                    #         previous_unit_cost * previous_qty + svl_dic["value"]
                    #     ) / previous_qty
                # Incoming or Outgoing moves without quantity and unit_cost
                elif not qty and svl.stock_move_id:
                    svl_dic["value"] = 0.0
            line.update_avco_svl_modified(preprocess_svl_dic, skip_avco_sync=False)
            # Reprocess svls to set manual adjust values take into account all vacuums
            self.process_avco_svl_manual_adjustements(svls_dic)
            # Update product standard price if it is modified
            if float_compare(
                previous_unit_cost,
                line.product_id.with_company(line.company_id.id).standard_price,
                precision_digits=precision_price,
            ):
                line.product_id.with_company(line.company_id.id).with_context(
                    disable_auto_svl=True
                ).sudo().standard_price = float_round(
                    previous_unit_cost, precision_digits=precision_price
                )
            # Update actual line value
            svl_dic = svls_dic[line]
            if svl_dic["quantity"] or svl_dic["unit_cost"]:
                svl_dic["value"] = svl_dic["quantity"] * svl_dic["unit_cost"]
            # Write changes in db
            line.update_avco_svl_modified(svls_dic)
            # Update unit_cost for incoming stock moves
            if (
                line.stock_move_id
                and line.stock_move_id._is_in()
                and float_compare(
                    line.stock_move_id.price_unit,
                    line.unit_cost,
                    precision_digits=precision_price,
                )
            ):
                line.stock_move_id.price_unit = line.unit_cost
