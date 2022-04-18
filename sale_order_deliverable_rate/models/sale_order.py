from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    deliverable_rate = fields.Float(
        compute="_compute_deliverable_rate",
        search="_search_deliverable_rate",
        digits="Sale order deliverable rate",
        store=False,
    )

    nb_order_line_need_delivery = fields.Float(
        compute="_compute_nb_order_line_need_delivery", store=False
    )

    def _get_order_lines_to_ship(self):
        self.ensure_one()
        return self.order_line.filtered(
            lambda line: not line.display_type
            and line.product_id.type == "product"
            and line.qty_to_ship > 0
        )

    @api.depends("order_line")
    def _compute_nb_order_line_need_delivery(self):
        for rec in self:
            rec.nb_order_line_need_delivery = len(rec._get_order_lines_to_ship())

    def _compute_deliverable_rate(self):
        for rec in self:

            if rec.nb_order_line_need_delivery > 0:
                rec.deliverable_rate = (
                    sum(rec._get_order_lines_to_ship().mapped("deliverable_rate"))
                    / rec.nb_order_line_need_delivery
                )
            else:
                # if everything is delivered deliverable rate => 0
                rec.deliverable_rate = 0

    def _search_deliverable_rate(self, operator, value):

        order_data = self.env["sale.order.line"].read_group(
            [("qty_to_ship", ">=", 0)], ["qty_to_ship"], ["order_id"]
        )
        order_ids = [data["order_id"][0] for data in order_data]
        orders = self.browse(order_ids)

        orders = orders.filtered_domain([("deliverable_rate", operator, value)])

        return [("id", "in", orders.ids)]
