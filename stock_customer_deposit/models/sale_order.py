# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_deposit = fields.Boolean()
    can_customer_deposit = fields.Boolean(related="warehouse_id.use_customer_deposits")
    customer_deposit_count = fields.Integer(compute="_compute_customer_deposit_count")

    @api.depends("warehouse_id", "partner_id")
    def _compute_customer_deposit_count(self):
        for order in self:
            if not order.warehouse_id.use_customer_deposits:
                order.customer_deposit_count = False
                continue
            order.customer_deposit_count = self.env["stock.quant"].search_count(
                order._get_customer_deposit_domain()
            )

    def _action_confirm(self):
        self._check_can_customer_deposit()
        deposit_lines = self.order_line.filtered(
            lambda line: line.deposit_available_qty > 0.0 and line.product_uom_qty > 0.0
        )
        if not deposit_lines:
            return super()._action_confirm()
        if deposit_lines.filtered(
            lambda line: line.route_id == line.warehouse_id.customer_deposit_route_id
        ):
            raise ValidationError(
                _(
                    "You can't use customer deposit for products with the route"
                    " 'Customer Deposit'."
                )
            )
        for order in self:
            deposit_lines = order.order_line.filtered(
                lambda line: line.deposit_available_qty > 0.0
                and line.product_uom_qty > 0.0
            )
            if not deposit_lines:
                continue
            quants_by_product = self.env["stock.quant"].read_group(
                domain=order._get_customer_deposit_domain(),
                fields=["available_quantity"],
                groupby=["product_id"],
            )
            product_deposit = {
                quant_by_product["product_id"][0]: quant_by_product[
                    "available_quantity"
                ]
                for quant_by_product in quants_by_product
            }
            for product in deposit_lines.mapped("product_id"):
                if product_deposit.get(product.id, 0.0) < sum(
                    deposit_lines.filtered(
                        lambda line: line.product_id.id == product.id
                    ).mapped("product_uom_qty")
                ):
                    raise ValidationError(
                        _(
                            "You can't add more than the quantity of %(product)s"
                            " from the customer's deposit. If the customer wants"
                            " more, create a new order after confirming this one.",
                            product=product.name,
                        )
                    )
        return super(SaleOrder, self)._action_confirm()

    def _check_can_customer_deposit(self):
        if self.filtered("customer_deposit").order_line.filtered(
            lambda line: line.product_id.type == "product"
            and line.route_id != line.warehouse_id.customer_deposit_route_id
        ):
            raise ValidationError(
                _(
                    "All lines coming from orders marked as 'Customer depot' must"
                    " have Customer deposit route."
                )
            )

        if self.order_line.filtered(
            lambda line: line.product_id.type == "product"
            and line.warehouse_id.customer_deposit_route_id
            and not line.order_id.customer_deposit
            and line.route_id == line.warehouse_id.customer_deposit_route_id
        ):
            raise ValidationError(
                _(
                    "You cannot select Customer Deposit route in an order line if you"
                    " do not mark the order as a customer depot."
                )
            )

    def _get_customer_deposit_domain(self):
        return [
            ("location_id.usage", "=", "internal"),
            ("warehouse_id", "in", self.warehouse_id.ids),
            ("quantity", ">", 0),
            ("owner_id", "!=", False),
            "|",
            "|",
            ("owner_id", "in", self.partner_id.ids),
            ("owner_id", "parent_of", self.partner_id.ids),
            ("owner_id", "child_of", self.partner_id.ids),
        ]

    def action_view_customer_deposits(self):
        domain = self._get_customer_deposit_domain()
        action = (
            self.env["stock.quant"]
            .with_context(no_at_date=True, search_default_on_hand=True)
            ._get_quants_action(domain)
        )
        action["name"] = _("Customer Deposits")
        return action
