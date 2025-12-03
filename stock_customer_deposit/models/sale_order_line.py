# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Turn it computable for the case of deposits
    route_id = fields.Many2one(compute="_compute_route_id", store=True, readonly=False)
    deposit_available_qty = fields.Float(
        readonly=True,
        digits="Product Unit of Measure",
        compute="_compute_deposit_available_qty",
        help="Quantity of the product available in customer deposit.",
    )
    deposit_allowed_qty = fields.Float(
        readonly=True,
        digits="Product Unit of Measure",
        compute="_compute_deposit_allowed_qty",
        help="Quantity of the product allowed to used in customer deposit.",
    )

    @api.depends("product_id", "warehouse_id", "order_id.customer_deposit")
    def _compute_route_id(self):
        res = None
        # Several modules might be converting the field into a compute, let's respect
        # inheritance
        if hasattr(super(), "_compute_route_id"):
            res = super()._compute_route_id()
        deposit_routes = (
            self.env["stock.warehouse"]
            .search([("use_customer_deposits", "=", True)])
            .customer_deposit_route_id
        )
        # Clear routes whenever we unset the order as deposit
        self.filtered(
            lambda x, deposit_routes=deposit_routes: x.route_id in deposit_routes
            and not x.order_id.customer_deposit
        ).route_id = False
        # Set the route automatically for deposits
        for line in self.filtered(
            lambda x: x.warehouse_id.use_customer_deposits
            and x.product_id.is_storable
            and x.order_id.customer_deposit
        ):
            line.route_id = line.warehouse_id.customer_deposit_route_id
        return res

    @api.depends("product_id", "order_partner_id", "warehouse_id")
    def _compute_deposit_available_qty(self):
        self.deposit_available_qty = False
        quants_by_product = (
            self.env["stock.quant"]
            .search_fetch(
                domain=self._get_customer_deposit_domain(),
                field_names=["available_quantity"],
            )
            .grouped("product_id")
        )
        if not quants_by_product:
            return
        for line in self.filtered(
            lambda x,
            quants_by_product=quants_by_product: x.warehouse_id.use_customer_deposits
            and x.product_id.is_storable
            and x.product_id in quants_by_product.keys()
        ):
            deposit_available_qty = sum(
                quants_by_product.get(line.product_id).mapped("available_quantity")
            )
            line.deposit_available_qty = deposit_available_qty

    @api.depends(
        "product_uom_qty",
        "deposit_available_qty",
    )
    def _compute_deposit_allowed_qty(self):
        for line in self:
            line.deposit_allowed_qty = line.deposit_available_qty - line.product_uom_qty

    @api.depends(
        "deposit_available_qty",
        "order_id.customer_deposit",
        "pricelist_item_id",
        "order_id.pricelist_id",
    )
    def _compute_discount(self):
        # Apply 100% discount when customer is taking from customer deposit
        res = super()._compute_discount()
        for line in self.filtered(
            lambda x: x.warehouse_id.use_customer_deposits
            and x.product_id.is_storable
            and not x.order_id.customer_deposit
        ):
            # TODO: We should take into account lines alredy placed for deposit so
            # we can mix them seamlessly
            if (
                float_compare(
                    line.deposit_available_qty,
                    0.0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0
            ):
                line.discount = 100.0
        return res

    @api.depends()
    def _compute_qty_to_invoice(self):
        # For deposits we'll override the invoice_policy
        # TODO: Improve invoiceability
        res = super()._compute_qty_to_invoice()
        for line in self.filtered(
            lambda x: not x.display_type
            and x.state == "sale"
            and x.route_id == x.warehouse_id.customer_deposit_route_id
            and x.warehouse_id.use_customer_deposits
        ):
            line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
        return res

    def _get_customer_deposit_domain(self):
        return [
            ("location_id.usage", "=", "internal"),
            ("warehouse_id", "in", self.warehouse_id.ids),
            ("product_id", "in", self.product_id.ids),
            ("quantity", ">", 0),
            "|",
            ("owner_id", "parent_of", self.order_partner_id.ids),
            ("owner_id", "child_of", self.order_partner_id.ids),
        ]

    def action_view_customer_deposits(self):
        action = (
            self.env["stock.quant"]
            .with_context(no_at_date=True, search_default_on_hand=True)
            ._get_quants_action(self._get_customer_deposit_domain())
        )
        action["name"] = self.env._("Customer Deposits")
        return action
