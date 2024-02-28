# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        sales_to_invoice = self.mapped("sale_id").filtered_domain(
            [
                ("invoice_status", "=", "to invoice"),
                ("invoice_frequency_id.automatic_picking_invoicing", "=", True),
            ]
        )
        if sales_to_invoice:
            invoices = sales_to_invoice._create_invoices()
            invoices.action_post()
        return res
