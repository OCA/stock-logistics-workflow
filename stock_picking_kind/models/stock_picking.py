# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_kind = fields.Selection(
        selection=[
            ("customer_return", "Customer Return"),
            ("customer_out", "Customer Delivery"),
            ("supplier_return", "Supplier Return"),
            ("supplier_in", "Supplier Reception"),
            ("drop_shipping", "Drop Shipping"),
            ("drop_shipping_return", "Drop Shipping Return"),
        ],
        compute="_compute_picking_kind",
        store=True,
        help="Indicate the kind of picking based on its locations",
    )

    @api.depends("location_id", "location_dest_id")
    def _compute_picking_kind(self):
        for rec in self:
            if (
                rec.location_id.usage == "supplier"
                and rec.location_dest_id.usage == "customer"
            ):
                rec.picking_kind = "drop_shipping"
            elif (
                rec.location_id.usage == "customer"
                and rec.location_dest_id.usage == "supplier"
            ):
                rec.picking_kind = "drop_shipping_return"
            elif (
                rec.location_id.usage == "customer"
                and rec.location_dest_id.usage != "customer"
            ):
                rec.picking_kind = "customer_return"
            elif (
                rec.location_id.usage != "customer"
                and rec.location_dest_id.usage == "customer"
            ):
                rec.picking_kind = "customer_out"
            elif (
                rec.location_id.usage == "supplier"
                and rec.location_dest_id.usage != "supplier"
            ):
                rec.picking_kind = "supplier_in"
            elif (
                rec.location_id.usage != "supplier"
                and rec.location_dest_id.usage == "supplier"
            ):
                rec.picking_kind = "supplier_return"
            else:
                rec.picking_kind = False
