# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict, OrderedDict

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


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
                svl.cost_price_avco_sync({})
        return svl

    def write(self, vals):
        """ Update cost price avco """
        svl_previous_vals = defaultdict(dict)
        if ("unit_cost" in vals or "quantity" in vals) and not self.env.context.get(
            "skip_avco_sync"
        ):
            for svl in self:
                for field_name in vals.keys():
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

    @api.model
    def get_avco_svl_qty_unit_cost(self, line, svl, vals):
        if svl.id == line.id:
            qty = vals.get("quantity", line.quantity)
            unit_cost = vals.get("unit_cost", line.unit_cost)
        else:
            qty = svl.quantity
            unit_cost = svl.unit_cost
        return qty, unit_cost

    @api.model
    def process_avco_svl_inventory(self, svl, svl_dic, line, svl_previous_vals, previous_unit_cost):
        high_decimal_precision = 8
        new_svl_qty = svl_dic["quantity"] + (svl_previous_vals[line.id]["quantity"] - line.quantity)
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
        # if update_enabled and "quantity" in vals:
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
    def get_avco_svl_price(self, previous_unit_cost, previous_qty, unit_cost, qty, total_qty):
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
            svls_dic.values()
        ):
            if not svl_to_vacuum["quantity"]:
                continue
            if abs(svl_to_vacuum["remaining_qty"]) <= vacuum_qty:
                vacuum_qty = vacuum_qty + svl_to_vacuum["remaining_qty"]
                diff_qty = -svl_to_vacuum["remaining_qty"]
                new_remaining_qty = 0.0
            else:
                new_remaining_qty = svl_to_vacuum["remaining_qty"] + vacuum_qty
                diff_qty = vacuum_qty
                vacuum_qty = 0.0
            vacuum_dic[svl_to_vacuum["id"]].append((diff_qty, self.unit_cost))
            # if svl.id != line.id:
            x = 0.0
            for q, c in vacuum_dic[svl_to_vacuum["id"]]:
                x += q * c
            if new_remaining_qty:
                x += abs(new_remaining_qty) * vacuum_dic[svl_to_vacuum["id"]][0][1]
            new_unit_cost = x / abs(svl_to_vacuum["quantity"])

            new_value = svl_to_vacuum["quantity"] * new_unit_cost
            svl_to_vacuum["remaining_qty"] = new_remaining_qty
            svl_to_vacuum["remaining_value"] = new_remaining_qty * new_unit_cost
            svl_to_vacuum["unit_cost"] = new_unit_cost
            svl_to_vacuum["value"] = new_value
            # Update remaining in incoming line
            svl_dic["remaining_qty"] = vacuum_qty
            svl_dic["remaining_value"] = vacuum_qty * svl_dic["unit_cost"]
            if vacuum_qty == 0.0:
                break

    def update_remaining_avco_svl_in(self, svls_dic):
        for svl in self:
            svl_dic = svls_dic[svl]
            svl_out_qty = svl_dic["quantity"]
            for svl_in_remaining in filter(
                lambda ln: ln["remaining_qty"] > 0,
                svls_dic.values()
            ):
                if abs(svl_out_qty) <= svl_in_remaining["remaining_qty"]:
                    new_remaining_qty = svl_in_remaining["remaining_qty"] + svl_out_qty
                    svl_out_qty = 0.0
                else:
                    svl_out_qty = svl_out_qty + svl_in_remaining["remaining_qty"]
                    new_remaining_qty = 0.0
                self.update_avco_svl_values(svl_in_remaining, remaining_qty=new_remaining_qty)
                if svl_out_qty == 0.0:
                    break

    def process_avco_svl_manual_adjustements(self, svls_dic, vals):
        for line in self:
            accumulated_qty = accumulated_value = 0.0
            for svl, svl_dic in svls_dic.items():
                if not svl_dic["quantity"] and not svl_dic["unit_cost"] and not svl.stock_move_id:
                    standard_price = float(svl.description.split(" ")[-1][:-1])
                    adjust_value = (
                        standard_price * accumulated_qty
                    ) - accumulated_value
                    if svl_dic["value"] != adjust_value:
                        svl_dic["value"] = adjust_value
                if svl.id == line.id:
                    accumulated_qty = accumulated_qty + vals.get("quantity", line.quantity)
                    accumulated_value = (
                        accumulated_value
                        + vals.get("unit_cost", line.unit_cost)
                        * vals.get("quantity", line.quantity)
                    )
                else:
                    accumulated_qty = accumulated_qty + svl_dic["quantity"]
                    accumulated_value = accumulated_value + svl_dic["value"]

    @api.model
    def update_avco_svl_modified(self, svls_dic):
        decimal_precision = 8
        for svl, svl_dic in svls_dic.items():
            vals = {}
            # Update unit cost
            if float_compare(svl["unit_cost"], svl_dic["unit_cost"], precision_rounding=svl.currency_id.rounding):
                vals["unit_cost"] = svl_dic["unit_cost"]
            # Update quantities
            if float_compare(svl["quantity"], svl_dic["quantity"], precision_digits=decimal_precision):
                vals["quantity"] = svl_dic["quantity"]
            if float_compare(svl["remaining_qty"], svl_dic["remaining_qty"], precision_digits=decimal_precision):
                vals["remaining_qty"] = svl_dic["remaining_qty"]
            # Update values
            if "quantity" in vals or "unit_cost" in vals or svl == self:
                vals["value"] = svl_dic["quantity"] * svl_dic["unit_cost"]
            if "remaining_qty" in vals or "unit_cost" in vals:
                vals["remaining_value"] = svl_dic["remaining_qty"] * svl_dic["unit_cost"]
            # Write modified fields
            if vals:
                svl.with_context(skip_avco_sync=True).write(vals)

    def cost_price_avco_sync(self, vals, svl_previous_vals={}):  # noqa: C901
        procesed_lines = set()
        dp_obj = self.env["decimal.precision"]
        precision_qty = dp_obj.precision_get("Product Unit of Measure")
        precision_price = dp_obj.precision_get("Product Price")
        for line in self.sorted(key=lambda l: (l.create_date, l.id)):
            if (
                line.id in procesed_lines
                or line.product_id.cost_method != "average"
                # or line.quantity < 0.0
            ):
                continue
            previous_unit_cost = previous_qty = 0.0
            # update_enabled determines if svl is after modified line to enable
            # write changes
            update_enabled = False
            svls_to_avco_sync = line.with_context(
                skip_avco_sync=True
            ).get_svls_to_avco_sync()
            vacuum_dic = defaultdict(list)
            inventory_processed = False
            unit_cost_processed = False
            svls_dic = OrderedDict()
            for svl in svls_to_avco_sync:
                qty, unit_cost = self.get_avco_svl_qty_unit_cost(line, svl, vals)
                svls_dic[svl] = {"id": svl.id, "quantity": qty, "unit_cost": unit_cost, "remaining_qty": qty, "remaining_value": qty * unit_cost}
                svl_dic = svls_dic[svl]
                # Keep inventory unit_cost if not previous incoming or manual adjustment
                if not unit_cost_processed:
                    previous_unit_cost = unit_cost
                f_compare = float_compare(qty, 0.0, precision_digits=precision_qty)
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
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        # Context to keep stock quantities after inventory qty update
                        and self.env.context.get("keep_avco_inventory", False)
                    ):
                        qty = self.process_avco_svl_inventory(
                            svl, svl_dic, line, svl_previous_vals, previous_unit_cost,
                        )
                        inventory_processed = True
                    else:
                        # TODO: Is necessary?
                        svl.update_avco_svl_values(svl_dic, unit_cost=previous_unit_cost)
                    # Check if adjust IN and we have moves to vacuum outs without stock
                    if (
                        update_enabled
                        and "quantity" in vals
                        and svl_dic["quantity"] > 0.0
                        and previous_qty < 0.0
                    ):
                        svl.vacumm_avco_svl(qty, svls_dic, vacuum_dic)
                    elif update_enabled and "quantity" in vals and svl_dic["quantity"] < 0.0:
                        svl.update_remaining_avco_svl_in(svls_dic)
                    previous_qty = previous_qty + qty
                # Incoming line in layer
                elif f_compare > 0:
                    total_qty = previous_qty + qty
                    # Return moves
                    if update_enabled and (not svl.stock_move_id or svl.stock_move_id.move_orig_ids):
                        svl.update_avco_svl_values(svl_dic, unit_cost=previous_unit_cost)
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
                    if previous_qty <= 0:
                        new_remaining_qty = qty
                    elif previous_qty < abs(qty):
                        new_remaining_qty = previous_qty + qty
                    else:
                        new_remaining_qty = 0.0
                    # Change (svl.remaining_qty - svl.quantity) to previous_qty?
                    vacuum_dic[svl.id].append(
                        (new_remaining_qty - svl_dic["quantity"], previous_unit_cost)
                    )
                    if update_enabled:
                        svl.update_avco_svl_values(
                            svl_dic,
                            unit_cost=previous_unit_cost,
                            remaining_qty=new_remaining_qty,
                        )
                    else:
                        svl.update_avco_svl_values(svl_dic, remaining_qty=new_remaining_qty)
                    previous_qty = previous_qty + qty
                    if update_enabled and "quantity" in vals and svl_dic["quantity"] < 0:
                        svl.update_remaining_avco_svl_in(svls_dic)
                # Manual standard_price adjustment line in layer
                elif not unit_cost and not qty and not svl.stock_move_id:
                    unit_cost_processed = True
                    standard_price = float(svl.description.split(" ")[-1][:-1])
                    # TODO: Review abs in previous_qty or new_diff
                    new_diff = standard_price - previous_unit_cost
                    svl_dic["value"] = new_diff * previous_qty
                    previous_unit_cost = standard_price
                # Enable update mode for after lines
                if svl.id == line.id:
                    update_enabled = True
                procesed_lines.add(svl.id)
            # Reprocess svls to set manual adjust values take into account all vacuums
            line.process_avco_svl_manual_adjustements(svls_dic, vals)
            # Update product standard price if it is modified
            if float_compare(
                previous_unit_cost,
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).standard_price,
                precision_digits=precision_price,
            ):
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).sudo().standard_price = float_round(
                    previous_unit_cost, precision_digits=precision_price)
            # Write changes in db
            line.update_avco_svl_modified(svls_dic)
            # Update unit_cost for incoming stock moves
            if line.stock_move_id:
                line.stock_move_id.price_unit = line.unit_cost
