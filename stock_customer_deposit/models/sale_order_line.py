# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    route_id = fields.Many2one(
        "stock.route", compute="_compute_route_id", store=True, readonly=False
    )
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

    @api.depends(
        "product_id", "warehouse_id.use_customer_deposits", "order_id.customer_deposit"
    )
    def _compute_route_id(self):
        for line in self:
            line.route_id = (
                line.warehouse_id.customer_deposit_route_id
                if line.warehouse_id.use_customer_deposits
                and line.product_id.type == "product"
                and line.order_id.customer_deposit
                else False
            )

    @api.depends("product_id", "order_partner_id", "warehouse_id")
    def _compute_deposit_available_qty(self):
        quants_by_product = self.env["stock.quant"].read_group(
            domain=self._get_customer_deposit_domain(),
            fields=["available_quantity"],
            groupby=["product_id"],
        )
        product_deposit = {
            line["product_id"][0]: line["available_quantity"]
            for line in quants_by_product
        }
        for line in self:
            if (
                not line.warehouse_id.use_customer_deposits
                or not line.product_id.type == "product"
            ):
                line.deposit_available_qty = 0.0
                continue
            line.deposit_available_qty = product_deposit.get(line.product_id.id, 0.0)

    @api.depends(
        "product_uom_qty",
        "deposit_available_qty",
    )
    def _compute_deposit_allowed_qty(self):
        for line in self:
            line.deposit_allowed_qty = line.deposit_available_qty - line.product_uom_qty

    @api.depends(
        "product_id", "product_uom", "product_uom_qty", "deposit_available_qty"
    )
    def _compute_discount(self):
        """Set discount to 100% if use_customer_deposit is True
        because customer paid before for them."""
        res = super()._compute_discount()
        for line in self:
            if line.deposit_available_qty:
                line.discount = 100.0
        return res

    @api.depends("qty_invoiced", "qty_delivered", "product_uom_qty", "state")
    def _compute_qty_to_invoice(self):
        res = super()._compute_qty_to_invoice()
        for line in self:
            if (
                line.warehouse_id.use_customer_deposits
                and line.state in ["sale", "done"]
                and not line.display_type
                and line.route_id
                and line.route_id == line.warehouse_id.customer_deposit_route_id
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
            "|",
            ("owner_id", "in", self.order_partner_id.ids),
            ("owner_id", "parent_of", self.order_partner_id.ids),
            ("owner_id", "child_of", self.order_partner_id.ids),
        ]

    def action_view_customer_deposits(self):
        action = (
            self.env["stock.quant"]
            .with_context(no_at_date=True, search_default_on_hand=True)
            ._get_quants_action(self._get_customer_deposit_domain())
        )
        action["name"] = _("Customer Deposits")
        return action
