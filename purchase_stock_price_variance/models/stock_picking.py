# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class Stockpick(models.Model):
    _inherit = "stock.picking"

    bypass_price_variance_check = fields.Boolean(
        copy=False,
        tracking=True,
        help="If enabled, no error is raised for price variance between "
        "the product's standard price and purchase receipt unit price.",
    )

    def write(self, vals):
        if "bypass_price_variance_check" in vals:
            if not self.env.user.has_group(
                "purchase_stock_price_variance.group_manage_price_variance_check"
            ):
                raise UserError(
                    _(
                        "You do not have permission to modify the "
                        "'Bypass Price Variance Check' field. "
                        "Please contact an administrator or a user "
                        "with the appropriate permissions."
                    )
                )
        return super().write(vals)

    def _action_done(self):
        company = self.env.company
        global_threshold_percent = company.price_variance_threshold_percent
        global_threshold_amount = company.price_variance_threshold_amount
        for pick in self:
            error_messages = []
            messages = []
            for move in pick.move_ids:
                if not (move._is_in() or move._is_dropshipped()):
                    continue
                product = move.product_id
                threshold_percent = (
                    product.price_variance_threshold_percent or global_threshold_percent
                )
                threshold_amount = (
                    product.price_variance_threshold_amount or global_threshold_amount
                )
                if not threshold_percent and not threshold_amount:
                    continue
                received_price = move._get_price_unit()
                standard_price = product.standard_price
                amount_difference = abs(received_price - standard_price)
                percentage_difference = (
                    (amount_difference / standard_price) * 100 if standard_price else 0
                )
                if (
                    threshold_percent and percentage_difference > threshold_percent
                ) or (threshold_amount and amount_difference > threshold_amount):
                    message = (
                        f"{product.name}: Received Price = {received_price}, "
                        f"Product Price = {standard_price}."
                    )
                    if (
                        not product.categ_id.bypass_price_variance_check
                        and not product.bypass_price_variance_check
                        and not pick.bypass_price_variance_check
                    ):
                        error_messages.append(message)
                    messages.append(message)

            def get_message(products, delimiter):
                message = _(
                    "Price variance exceeding a threshold detected for the following products:"
                )
                return message + delimiter + delimiter.join(products)

            if pick.company_id.enable_price_variance_error and error_messages:
                raise UserError(get_message(error_messages, "\n"))
            if messages:
                pick.message_post(body=get_message(messages, "<br/>"))
        return super()._action_done()
