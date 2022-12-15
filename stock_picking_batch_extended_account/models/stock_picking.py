# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        result = super()._action_done()
        picking_to_invoice_ids = self.env.context.get(
            "picking_to_invoice_in_batch",
        )
        if not picking_to_invoice_ids:
            return result
        sales = self.filtered(lambda r: r.id in picking_to_invoice_ids).mapped(
            "sale_id"
        )
        sales_to_invoice = sales.filtered(lambda so: so.invoice_status == "to invoice")
        if not sales_to_invoice:
            return result
        self.env["sale.advance.payment.inv"].create({}).with_context(
            active_model="sale.order", active_ids=sales_to_invoice.ids
        ).create_invoices()
        sales_to_invoice.mapped("invoice_ids").filtered(
            lambda r: r.state == "draft",
        ).action_post()
        return result
