# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import OR
from odoo.tools import float_compare, float_is_zero

from odoo.addons.stock.models.product import OPERATORS


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    location_ids = fields.Many2many(
        "stock.location",
        compute="_compute_location_qty",
        string="Locations",
    )
    qty_available = fields.Float(
        compute="_compute_location_qty",
        search="_search_qty_available",
        string="Qty. Available",
    )

    @api.depends(
        "quant_ids",
        "quant_ids.location_id",
        "quant_ids.quantity",
        "quant_ids.reserved_quantity",
    )
    def _compute_location_qty(self):
        for lot in self:
            # Same logic as method _product_qty of stock
            quants = lot.quant_ids.filtered(
                lambda q: q.location_id.usage == "internal"
                or (q.location_id.usage == "transit" and q.location_id.company_id)
            )
            lot.location_ids = quants.mapped("location_id")
            lot.qty_available = sum(quants.mapped("quantity")) - sum(
                quants.mapped("reserved_quantity")
            )

    def _search_qty_available(self, operator, value):
        # See: stock_lot_product_qty_search
        if operator not in ("<", ">", "=", "!=", "<=", ">="):
            raise UserError(_("Invalid domain operator %s", operator))
        if not isinstance(value, (float, int)):
            raise UserError(_("Invalid domain right operand %s", value))
        # Check if we should include lots with a quantity of 0 in the results
        uom_precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        include_without_qty = (
            operator == "<"
            and float_compare(value, 0, precision_digits=uom_precision) > 0
            or operator == "<="
            and float_compare(value, 0, precision_digits=uom_precision) >= 0
            or operator == ">"
            and float_compare(value, 0, precision_digits=uom_precision) < 0
            or operator == ">="
            and float_compare(value, 0, precision_digits=uom_precision) <= 0
            or operator == "="
            and float_is_zero(value, precision_digits=uom_precision)
            or operator == "!="
            and not float_is_zero(value, precision_digits=uom_precision)
        )

        locations_domain = OR(
            [
                [("usage", "=", "internal")],
                [("usage", "=", "transit"), ("company_id", "!=", False)],
            ]
        )
        quants_locations = self.env["stock.location"].search(locations_domain)
        grouped_quants = self.env["stock.quant"].read_group(
            [("lot_id", "!=", False), ("location_id", "in", quants_locations.ids)],
            ["lot_id", "quantity", "reserved_quantity"],
            ["lot_id"],
            orderby="id",
        )
        lot_ids_with_quantity = {
            group["lot_id"][0]: group["quantity"] - group["reserved_quantity"]
            for group in grouped_quants
        }
        if include_without_qty:
            lot_ids_without_qty = self.search(
                [("id", "not in", list(lot_ids_with_quantity.keys()))]
            ).ids
            lot_ids_with_quantity.update({lot_id: 0 for lot_id in lot_ids_without_qty})
        res_ids = [
            lot_id
            for lot_id, quantity in lot_ids_with_quantity.items()
            if OPERATORS[operator](quantity, value)
        ]
        return [("id", "in", res_ids)]
