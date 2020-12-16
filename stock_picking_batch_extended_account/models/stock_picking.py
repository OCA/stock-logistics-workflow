# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        result = super().action_done()
        picking_to_invoice_ids = self.env.context.get(
            "picking_to_invoice_in_batch",
        )
        if not picking_to_invoice_ids:
            return result
        sales = self.filtered(
            lambda r: r.id in picking_to_invoice_ids,
        ).mapped("sale_id")
        self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'all',
        }).with_context(active_ids=sales.ids).create_invoices()
        sales.mapped("invoice_ids").filtered(
            lambda r: r.state == "draft",
        ).action_invoice_open()
        return result
