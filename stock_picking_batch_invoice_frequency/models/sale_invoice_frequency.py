# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class SaleInvoiceFrequency(models.Model):
    _inherit = "sale.invoice.frequency"

    automatic_batch_invoicing = fields.Boolean(
        help="If checked, the invoices will be created and posted "
        "in stock picking batches when validated."
    )
