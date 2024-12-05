# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


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
        for order in self.filtered(lambda o: not o.customer_deposit):
            deposit_lines = order.order_line.filtered(
                lambda line: not line.display_type
                and float_compare(
                    line.deposit_available_qty,
                    0.0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0
                and float_compare(
                    line.product_uom_qty,
                    0.0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0
            )
            # Normal order
            if not deposit_lines:
                continue
            # Taking from deposit order
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
                if (
                    float_compare(
                        product_deposit.get(product.id, 0.0),
                        sum(
                            deposit_lines.filtered(
                                lambda line: line.product_id.id == product.id
                            ).mapped("product_uom_qty")
                        ),
                        precision_rounding=product.uom_id.rounding,
                    )
                    < 0
                ):
                    raise ValidationError(
                        _(
                            "You're trying to sell more than what's available "
                            "in the customer's deposit for '%(product)s'.\n"
                            "You can either adjust the quantity to fit what's "
                            "available or create a new order to increase the "
                            "deposit before proceeding.",
                            product=product.name,
                        )
                    )
        return super()._action_confirm()

    def _check_can_customer_deposit(self):
        """Check if the order is valid to perform a deposit or take from deposit"""
        for order in self:
            product_lines = order.order_line.filtered(
                lambda line: line.product_id.type == "product"
            )
            if order.customer_deposit:
                # Perform deposit
                if product_lines.filtered(
                    lambda line: line.route_id
                    != line.warehouse_id.customer_deposit_route_id
                ):
                    raise ValidationError(
                        _(
                            "All lines coming from orders marked as 'Customer depot' must"
                            " have Customer deposit route."
                        )
                    )
            elif order.warehouse_id.customer_deposit_route_id:
                # Take from deposit
                if product_lines.filtered(
                    lambda line: line.route_id
                    == line.warehouse_id.customer_deposit_route_id
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
