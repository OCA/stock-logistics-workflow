# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, time

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    # related field to manage closed lines
    active = fields.Boolean(default=True)

    def _get_purchase_price_unit(self):
        self.ensure_one()
        invoice_lines = self.env["stock.move.line"]._get_right_invoice_lines(
            self.purchase_line_id
        )
        if invoice_lines and invoice_lines[0].move_id.state == "posted":
            # In real life, all move lines related to an 1 invoice line
            # should be in the same state and have the same date
            inv_line = invoice_lines[0]
            # add a check for bad inserted values in invoices (like invoice
            # a lot of purchased products with 1 in quantity)
            inv_quantity = inv_line.quantity
            total_inv_quantity = sum(invoice_lines.mapped("quantity"))
            purchase_quantity = self.purchase_line_id.product_uom_qty
            if inv_quantity < purchase_quantity > total_inv_quantity:
                inv_quantity = purchase_quantity
            invoice = inv_line.move_id
            price_unit = invoice.currency_id._convert(
                inv_line.price_subtotal,
                invoice.company_id.currency_id,
                invoice.company_id,
                invoice.date or fields.Date.today(),
            ) / (inv_quantity or 1)
        else:
            # get price from purchase line
            purchase = self.purchase_line_id.order_id
            price_unit = purchase.currency_id._convert(
                self.purchase_line_id.price_subtotal,
                purchase.company_id.currency_id,
                purchase.company_id,
                purchase.date_order or fields.Date.today(),
            ) / (
                self.purchase_line_id.product_qty
                if self.purchase_line_id.product_qty != 0
                else 1
            )
        return price_unit or 0.0


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # add field to manage closed lines
    active = fields.Boolean(related="move_id.active", store=True, default=True)
    company_id = fields.Many2one(related="move_id.company_id", store=True)

    def _get_last_closing(self, closing_id, product_id, company_id):
        # default value
        start_qty = 0
        start_price = 0

        if closing_id.last_closed_id:
            last_closed_id = closing_id.last_closed_id
            # search product
            closing_line_id = self.env["stock.close.period.line"].search(
                [("close_id", "=", last_closed_id.id), ("product_id", "=", product_id)],
                limit=1,
            )
            if closing_line_id:
                start_qty = closing_line_id.product_qty
                start_price = closing_line_id.price_unit

        return start_qty, start_price

    @api.model
    def _get_right_invoice_lines(self, purchase_line_id):
        invoice_lines = purchase_line_id.invoice_lines.filtered(
            lambda il: il.move_id.is_purchase_document()
        )
        if "rc_original_purchase_invoice_ids" in self.env["account.move"].fields_get():
            rc_original_purchase_invoice_ids = invoice_lines.mapped(
                "move_id.rc_original_purchase_invoice_ids"
            )
            invoice_lines = invoice_lines.filtered(
                lambda il: il.move_id.id in rc_original_purchase_invoice_ids.ids
            )
        return invoice_lines

    def _get_additional_landed_cost_new(self, move_id, company_id):
        # function meant to be overriden
        return 0

    @api.model
    def _get_cost_stock_move_purchase_average(self, last_close_date, closing_line_id):
        product_id = closing_line_id.product_id
        company_id = closing_line_id.close_id.company_id.id
        min_date = datetime.combine(last_close_date, time.min)
        max_date = datetime.combine(closing_line_id.close_id.close_date, time.max)

        # get all moves (exclude by default inventory moves)
        move_ids = self.env["stock.move"].search(
            [
                ("state", "=", "done"),
                ("product_qty", ">", 0),
                ("product_id", "=", product_id.id),
                ("date", ">", min_date),
                ("date", "<=", max_date),
                ("active", ">=", 0),
                ("company_id", "=", company_id),
                ("location_id.usage", "!=", "inventory"),
                ("location_dest_id.usage", "!=", "inventory"),
            ],
            order="date",
        )

        # get start data from last close
        start_qty, start_price = self._get_last_closing(
            closing_line_id.close_id, product_id.id, company_id
        )
        if start_qty:
            inventory_amount = start_price * start_qty
            inventory_qty = start_qty
        else:
            inventory_amount = 0
            inventory_qty = 0

        cumulative_amount = 0
        cumulative_landed_cost = 0
        cumulative_qty = 0
        for move_id in move_ids.filtered(lambda m: m.purchase_line_id):
            invoice_lines = self._get_right_invoice_lines(move_id.purchase_line_id)
            if invoice_lines:
                cumulative_amount += sum(abs(line.balance) for line in invoice_lines)
                cumulative_qty += sum(invoice_lines.mapped("quantity"))
            elif (
                move_id.purchase_line_id.currency_id
                == move_id.purchase_line_id.company_id.currency_id
            ):
                price = move_id.purchase_line_id.price_unit
                cumulative_amount += move_id.purchase_line_id.product_uom_qty * price
                cumulative_qty += move_id.purchase_line_id.product_uom_qty
            else:
                price = move_id.purchase_line_id.currency_id._convert(
                    move_id.purchase_line_id.price_unit,
                    move_id.purchase_line_id.company_id.currency_id,
                    move_id.purchase_line_id.company_id,
                    move_id.date,
                    False,
                )
                cumulative_amount += move_id.purchase_line_id.product_uom_qty * price
                cumulative_qty += move_id.purchase_line_id.product_uom_qty

            additional_landed_cost_new = self._get_additional_landed_cost_new(
                move_id, company_id
            )
            cumulative_landed_cost += additional_landed_cost_new

        if (cumulative_qty + inventory_qty) != 0:
            price_unit = (
                inventory_amount + cumulative_amount + cumulative_landed_cost
            ) / (cumulative_qty + inventory_qty)
        else:
            price_unit = 0

        if price_unit == 0:
            closing_line_id.price_unit = product_id._get_cost()
            closing_line_id.evaluation_method = "standard"
        else:
            closing_line_id.price_unit = price_unit
            closing_line_id.inventory_amount = inventory_amount
            closing_line_id.inventory_qty = inventory_qty
            closing_line_id.cumulative_amount = cumulative_amount
            closing_line_id.cumulative_landed_cost = cumulative_landed_cost
            closing_line_id.cumulative_qty = cumulative_qty
            closing_line_id.evaluation_method = "purchase"

    def _get_cost_stock_move_standard(self, closing_line_id):
        closing_line_id.price_unit = closing_line_id.product_id._get_cost()
        closing_line_id.evaluation_method = "standard"

    def _check_consistency(self, closing_line_id):
        """
        Check inconsistency before elaborate closing line
        :return: True if line is consistency else False
        """
        return True

    @api.model
    def _search_same_product_value(self, closing_line_id):
        other_closing_line_id = self.env["stock.close.period.line"].search(
            [
                ("close_id", "=", closing_line_id.close_id.id),
                ("product_id", "=", closing_line_id.product_id.id),
                ("price_unit", "!=", 0),
            ],
            limit=1,
        )
        closing_line_id.price_unit = other_closing_line_id.price_unit
        closing_line_id.inventory_amount = other_closing_line_id.inventory_amount
        closing_line_id.inventory_qty = other_closing_line_id.inventory_qty
        closing_line_id.cumulative_amount = other_closing_line_id.cumulative_amount
        closing_line_id.cumulative_landed_cost = (
            other_closing_line_id.cumulative_landed_cost
        )
        closing_line_id.cumulative_qty = other_closing_line_id.cumulative_qty
        closing_line_id.evaluation_method = other_closing_line_id.evaluation_method
        self.env.cr.commit()  # pylint: disable=E8102

    @api.model
    def _evaluate_product(
        self, closing_id, closing_line_id, last_close_date, product_id
    ):
        if (
            closing_id.force_evaluation_method != "no_force"
            and not closing_line_id.evaluation_method
        ):
            if closing_id.force_evaluation_method == "purchase":
                self._get_cost_stock_move_purchase_average(
                    last_close_date, closing_line_id
                )
            if closing_id.force_evaluation_method == "standard":
                self._get_cost_stock_move_standard(closing_line_id)
        else:
            if product_id.categ_id.property_cost_method in ["average", "fifo"]:
                self._get_cost_stock_move_purchase_average(
                    last_close_date, closing_line_id
                )
            if product_id.categ_id.property_cost_method == "standard":
                self._get_cost_stock_move_standard(closing_line_id)

    def _recompute_cost_stock_move_purchase(self, closing_id):
        _logger.info("[1/2] Start recompute cost product purchase")

        # search only lines not elaborated
        closing_line_ids = self.env["stock.close.period.line"].search(
            [
                ("close_id", "=", closing_id.id),
                ("evaluation_method", "not in", ["manual"]),
                # ("product_qty", ">", 0),  # all products must be present to compute
                # other lines values
                # ("price_unit", "=", 0),
            ]
        )

        last_close_date = closing_id.last_close_date

        # all closing line ready to elaborate
        elaborated_products = self.env["product.product"]
        for closing_line_id in closing_line_ids:
            if not self._check_consistency(closing_line_id):
                continue
            product_id = closing_line_id.product_id
            if product_id.id in elaborated_products.ids:
                self._search_same_product_value(closing_line_id)
                continue
            elaborated_products |= product_id

            self._evaluate_product(
                closing_id, closing_line_id, last_close_date, product_id
            )

            self.env.cr.commit()  # pylint: disable=E8102
        _logger.info("[1/2] Finish recompute average cost product")

    def _write_results(self, closing_id):
        decimal = self.env["decimal.precision"].precision_get("Product Price")

        _logger.info("[2/2] Start writing results")

        # compute amount
        amount = 0
        for closing_line_id in closing_id.line_ids:
            row_value = (
                closing_line_id.product_qty if closing_line_id.product_qty > 0 else 0
            ) * closing_line_id.price_unit
            amount += round(row_value, decimal)

        # set amount closing
        closing_id.amount = amount

        _logger.info("[2/2] Finish writing results")

    def recompute_average_cost_period_purchase(self, closing_id):
        _logger.info("Recompute average cost period. Making in 2 phases:")
        _logger.info("[1/2] Recompute cost product purchase")
        _logger.info("[2/2] Write results")

        self._recompute_cost_stock_move_purchase(closing_id)
        self._write_results(closing_id)

        _logger.info("End recompute average cost product")
