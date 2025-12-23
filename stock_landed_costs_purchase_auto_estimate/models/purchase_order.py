from odoo import fields, models
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_estimated_cost_line_vals(self, line, cost_price):
        """Legacy cost line: the purchased product, forced to the stock
        valuation account, so the estimate entry nets within that account."""
        return {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "account_id": line.product_id.product_tmpl_id.get_product_accounts()[
                "stock_valuation"
            ].id,
            "price_unit": cost_price,
            "split_method": line.product_id.split_method_landed_cost or "equal",
        }

    def _prepare_estimated_cost_product_line_vals(self, total):
        """Single cost line on the configured estimated-landed-cost product.

        ``account_id`` is deliberately left empty: the landed-cost posting
        then falls back to the product's expense account (e.g. a freight
        account), so the estimate is posted as a debit on the goods' stock
        valuation account and a credit on the freight account — the same
        account the actual freight invoice debits later, whose balance
        therefore becomes the estimate-vs-actual variance.
        """
        product = self.company_id.estimated_landed_cost_product_id
        return {
            "product_id": product.id,
            "name": product.name,
            "price_unit": total,
            "split_method": product.split_method_landed_cost or "by_current_cost_price",
        }

    def _create_picking_with_stock_landed_cost(self, picking):
        res = super()._create_picking_with_stock_landed_cost(picking)
        # sudo() is needed because only Inventory > Administrator has
        # permissions on stock.landed.cost (see base module)
        landed_cost = self.sudo().landed_cost_ids[-1]
        lc_product = self.company_id.estimated_landed_cost_product_id
        company_currency = self.company_id.currency_id
        total_estimate = 0.0
        # we add the cost lines based on estimates
        for line in picking.mapped("move_ids.purchase_line_id"):
            if line.order_id.partner_id not in line.product_id.seller_ids.mapped(
                "partner_id"
            ):
                continue
            # estimated cost is based on the po price and the estimated indirect cost
            # in the supplierinfo
            supplierinfo = line.product_id.seller_ids.filtered(
                lambda x, line=line: x.partner_id == line.order_id.partner_id
            )
            if not supplierinfo:
                continue
            supplierinfo = supplierinfo[0]
            if line.product_id.cost_method not in ("fifo", "average"):
                continue
            cost_price = line.currency_id._convert(
                line.price_subtotal * supplierinfo.indirect_cost_percent / 100,
                company_currency,
                line.company_id,
                line.date_planned or fields.Date.context_today(line),
            )
            if float_is_zero(cost_price, precision_rounding=company_currency.rounding):
                continue
            if lc_product:
                total_estimate += cost_price
            else:
                landed_cost.cost_lines = [
                    (0, 0, self._prepare_estimated_cost_line_vals(line, cost_price))
                ]
        if lc_product and not float_is_zero(
            total_estimate, precision_rounding=company_currency.rounding
        ):
            landed_cost.cost_lines = [
                (0, 0, self._prepare_estimated_cost_product_line_vals(total_estimate))
            ]
        if not landed_cost.cost_lines:
            # if estimate is zero don't keep empty LC
            landed_cost.unlink()
        return res
