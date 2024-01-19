# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    batch_print_invoices = fields.Boolean(
        "Print Invoices from batch",
        help="Check this box to print all the invoices associated with the pickings"
        " contained in a picking batch.",
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
