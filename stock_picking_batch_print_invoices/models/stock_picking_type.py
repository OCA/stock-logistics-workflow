# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    print_documents_from_batch = fields.Selection(
        selection_add=[
            ("invoices", "Invoices"),
            ("invoices_and_pickings", "Invoices and Pickings"),
            ("invoices_or_pickings", "Invoices or Pickings"),
        ],
        help="'Pickings': Print only pickings are in batch.\n"
        "'Invoices': Print only invoices related with pickings are in batch.\n"
        "'Invoices and Pickings': Print pickings are in batch and invoices related"
        " with pickings are in batch.\n"
        "'Invoices or Pickings': Print invoices related with pickings are in batch"
        " but if picking has not invoice, then print picking.",
    )
    number_copies_invoices = fields.Integer(
        "Number of copies per invoice",
        default=1,
    )

    @api.constrains("number_copies_invoices")
    def _check_number_copies_invoices(self):
        for record in self:
            if record.number_copies_invoices < 0:
                raise ValidationError(
                    _("The number of copies per invoice must be greater or equal to 0")
                )
