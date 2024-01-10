# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        if self.env.context.get("invoice_batch", False):
            sales = self.mapped("sale_id").filtered(
                lambda so: so.invoice_status == "to invoice"
                and so.invoice_frequency_id.automatic_batch_invoicing
            )
            if sales:
                invoices = sales._create_invoices()
                invoices.action_post()
        return res
