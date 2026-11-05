# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    route_ids = fields.Many2many(
        comodel_name="stock.route",
        string="Routes",
        domain=[("sale_selectable", "=", True)],
        help="When you change this field all the lines will be changed."
        " After use it you will be able to change each line.",
    )

    @api.onchange("route_ids")
    def _onchange_route_ids(self):
        """We could do sale order line route_ids field compute store writable.
        But this field is created by Odoo so I prefer not modify it.
        """
        self.order_line.route_ids = self.route_ids

    def write(self, vals):
        res = super().write(vals)
        if "route_ids" in vals:
            lines = self.mapped("order_line").filtered(
                lambda line: line.route_ids.ids != vals["route_ids"]
            )
            lines.write({"route_ids": vals["route_ids"]})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders.filtered("route_ids"):
            order.order_line.filtered(
                lambda line: not line.route_ids
            ).route_ids = order.route_ids
        return orders


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def global_stock_route_product_id_change(self):
        if self.order_id.route_ids:
            self.route_ids = self.order_id.route_ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("route_ids") and vals.get("order_id"):
                order = self.env["sale.order"].browse(vals["order_id"])
                if order.route_ids:
                    vals["route_ids"] = [(6, 0, order.route_ids.ids)]
        return super().create(vals_list)
