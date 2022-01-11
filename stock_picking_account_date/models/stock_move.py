# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


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
        """
        This method overrides the parent method to force the period date to be the
        accounting date of the picking.
        """
        new_self = self.with_context(force_period_date=self.picking_id.accounting_date or fields.Date.context_today(self))
        return super(StockMove, new_self)._prepare_account_move_vals(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost,
        )

    def _get_price_unit(self):
        """
        Compute the price unit for the stock move based on the purchase line's price
        unit and taxes.
        If the purchase line's currency is different from the company's currency, the
        price unit is converted to the company's currency using the accounting date of
        the picking.
        """
        if (
            self.picking_id.accounting_date
            and self.purchase_line_id
            and self.purchase_line_id.order_id.currency_id
            != self.company_id.currency_id
        ):
            price_unit = self.purchase_line_id.taxes_id.with_context(
                round=False
            ).compute_all(
                self.purchase_line_id.price_unit,
                currency=self.purchase_line_id.order_id.currency_id,
                quantity=1.0,
                product=self.purchase_line_id.product_id,
                partner=self.purchase_line_id.order_id.partner_id,
            )[
                "total_excluded"
            ]
            price_unit = self.purchase_line_id.product_uom._compute_quantity(
                price_unit, self.product_uom, round=False
            )
            price_unit = self.purchase_line_id.order_id.currency_id._convert(
                price_unit,
                self.company_id.currency_id,
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
