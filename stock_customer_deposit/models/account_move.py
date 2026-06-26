# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from collections import defaultdict

from odoo import models
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoiced_lot_values(self):
        # This function is almost a copy of:
        # sale_stock/models/account_move.py:AccountMove._get_invoiced_lot_values
        self.ensure_one()
        res = super(AccountMove, self)._get_invoiced_lot_values()

        if (
            self.state == "draft"
            or not self.invoice_date
            or self.move_type not in ("out_invoice", "out_refund")
        ):
            return res

        current_invoice_amls = self.invoice_line_ids.filtered(
            lambda aml: aml.display_type == "product"
            and aml.product_id
            and aml.product_id.type in ("consu", "product")
            and aml.quantity
        )
        all_invoices_amls = current_invoice_amls.sale_line_ids.invoice_lines.filtered(
            lambda aml: aml.move_id.state == "posted"
        ).sorted(lambda aml: (aml.date, aml.move_name, aml.id))
        index = (
            all_invoices_amls.ids.index(current_invoice_amls[:1].id)
            if current_invoice_amls[:1] in all_invoices_amls
            else 0
        )
        previous_amls = all_invoices_amls[:index]
        invoiced_qties = current_invoice_amls._get_invoiced_qty_per_product()
        invoiced_products = invoiced_qties.keys()

        if self.move_type == "out_invoice":
            # filter out the invoices that have been fully refund and
            # re-invoice otherwise, the quantities would be
            # consumed by the reversed invoice and won't be print
            # on the new draft invoice
            previous_amls = previous_amls.filtered(
                lambda aml: aml.move_id.payment_state != "reversed"
            )

        previous_qties_invoiced = previous_amls._get_invoiced_qty_per_product()

        if self.move_type == "out_refund":
            # we swap the sign because it's a refund,
            # and it would print negative number otherwise
            for p in previous_qties_invoiced:
                previous_qties_invoiced[p] = -previous_qties_invoiced[p]
            for p in invoiced_qties:
                invoiced_qties[p] = -invoiced_qties[p]

        qties_per_lot = defaultdict(float)
        previous_qties_delivered = defaultdict(float)
        # Select Deposit moves
        stock_move_lines = (
            current_invoice_amls.sale_line_ids.filtered_domain(
                [
                    # Select orders with customer deposit
                    ("order_id.customer_deposit", "=", True),
                ]
            )
            .mapped("move_ids")
            .filtered(
                # Select moves with deposit routes
                lambda sm: sm.warehouse_id.customer_deposit_route_id
                in sm.route_ids
            )
            .mapped("move_line_ids")
            .filtered(lambda sml: sml.state == "done" and sml.lot_id)
            .sorted(lambda sml: (sml.date, sml.id))
        )
        for sml in stock_move_lines:
            warehouse = sml.move_id.warehouse_id
            if sml.product_id not in invoiced_products:
                continue
            # Check route of the move matches the route of the warehouse
            if warehouse.customer_deposit_route_id not in sml.move_id.route_ids:
                continue
            product = sml.product_id
            product_uom = product.uom_id
            qty_done = sml.product_uom_id._compute_quantity(sml.qty_done, product_uom)

            # is it a stock return considering the document type
            # (should it be it thought of as positively or negatively?)
            # min(qty, invoiced_qties[lot.product_id]) after
            is_stock_return = (
                self.move_type == "out_invoice"
                and sml.picking_id
                == warehouse.customer_deposit_type_id.return_picking_type_id
                or self.move_type == "out_refund"
                and sml.picking_id == warehouse.customer_deposit_type_id
            )
            if is_stock_return:
                returned_qty = min(qties_per_lot[sml.lot_id], qty_done)
                qties_per_lot[sml.lot_id] -= returned_qty
                qty_done = returned_qty - qty_done

            previous_qty_invoiced = previous_qties_invoiced[product]
            previous_qty_delivered = previous_qties_delivered[product]
            # If we return more than currently delivered (i.e., qty_done < 0),
            #  we remove the surplus from the previously delivered
            # (and qty_done becomes zero). If it's a delivery, we first
            # try to reach the previous_qty_invoiced
            if (
                float_compare(qty_done, 0, precision_rounding=product_uom.rounding) < 0
                or float_compare(
                    previous_qty_delivered,
                    previous_qty_invoiced,
                    precision_rounding=product_uom.rounding,
                )
                < 0
            ):
                previously_done = (
                    qty_done
                    if is_stock_return
                    else min(previous_qty_invoiced - previous_qty_delivered, qty_done)
                )
                previous_qties_delivered[product] += previously_done
                qty_done -= previously_done
            qties_per_lot[sml.lot_id] += qty_done

        for lot, qty in qties_per_lot.items():
            # access the lot as a superuser in order to avoid an error
            # when a user prints an invoice without having the stock access
            lot = lot.sudo()
            if (
                float_is_zero(
                    invoiced_qties[lot.product_id],
                    precision_rounding=lot.product_uom_id.rounding,
                )
                or float_compare(qty, 0, precision_rounding=lot.product_uom_id.rounding)
                <= 0
            ):
                continue
            invoiced_lot_qty = min(qty, invoiced_qties[lot.product_id])
            invoiced_qties[lot.product_id] -= invoiced_lot_qty
            res.append(
                {
                    "product_name": lot.product_id.display_name,
                    "quantity": formatLang(
                        self.env, invoiced_lot_qty, dp="Product Unit of Measure"
                    ),
                    "uom_name": lot.product_uom_id.name,
                    "lot_name": lot.name,
                    # The lot id is needed by localizations to inherit the method
                    # and add custom fields on the invoice's report.
                    "lot_id": lot.id,
                }
            )

        return res
