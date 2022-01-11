# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(
        self,
        credit_account_id,
        debit_account_id,
        journal_id,
        qty,
        description,
        svl_id,
        cost,
    ):
        if self.picking_id.accounting_date:
            context = dict(self.env.context)
            context["force_period_date"] = self.picking_id.accounting_date
            self = self.with_context(**context)
        return super()._prepare_account_move_vals(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost,
        )

    def _get_price_unit(self):
        if self.picking_id.accounting_date and self.purchase_line_id:
            po_line = self.purchase_line_id
            order = po_line.order_id
            price_unit = po_line.price_unit
            if po_line.taxes_id:
                price_unit = po_line.taxes_id.with_context(round=False).compute_all(
                    price_unit,
                    currency=order.currency_id,
                    quantity=1.0,
                    product=po_line.product_id,
                    partner=order.partner_id,
                )["total_excluded"]
            if po_line.product_uom.id != po_line.product_id.uom_id.id:
                price_unit *= (
                    po_line.product_uom.factor / po_line.product_id.uom_id.factor
                )
            if order.currency_id != order.company_id.currency_id:
                price_unit = order.currency_id._convert(
                    price_unit,
                    order.company_id.currency_id,
                    self.company_id,
                    self.picking_id.accounting_date,
                    round=False,
                )
            self.write(
                {
                    "price_unit": price_unit,
                    "date": self.picking_id.accounting_date,
                }
            )
            return price_unit
        return super()._get_price_unit()
