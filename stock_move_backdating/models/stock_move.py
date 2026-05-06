# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

from .stock_move_line import check_date


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """Set date for convert price unit multi currency."""
        self.ensure_one()
        price_unit = super()._get_price_unit()
        date_backdating = self.env.context.get("date_backdating", False)
        if (
            hasattr(self, "purchase_line_id")
            and date_backdating
            and not self.origin_returned_move_id
            and self.purchase_line_id
            and self.product_id.id == self.purchase_line_id.product_id.id
        ):
            line = self.purchase_line_id
            order = line.order_id
            converted_price = line.price_unit
            if order.currency_id != order.company_id.currency_id:
                converted_price = order.currency_id._convert(
                    converted_price,
                    order.company_id.currency_id,
                    order.company_id,
                    date_backdating,
                    round=False,
                )
            return {self.env["stock.lot"]: converted_price}
        return price_unit

    def _action_done(self, cancel_backorder=False):
        # Pass the (first) backdating date through the context so that
        # _create_account_move uses force_period_date when creating the
        # account move during super(). The actual move/move_line dates are
        # then re-applied at picking level after super() completes.
        move_lines_with_date = self.move_line_ids.filtered("date_backdating")
        if move_lines_with_date:
            date_backdating = move_lines_with_date[:1].date_backdating
            check_date(self, date_backdating)
            self = self.with_context(
                date_backdating=date_backdating,
                force_period_date=date_backdating.date(),
            )
        return super()._action_done(cancel_backorder=cancel_backorder)
