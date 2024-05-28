# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    print_documents_from_batch = fields.Selection(
        [("pickings", "Pickings")], default=False
    )
    number_copies_pickings = fields.Integer(
        "Number of copies",
        help="Number of copies per picking",
        default=1,
    )

    @api.constrains("number_copies_pickings")
    def _check_number_copies_pickings(self):
        for record in self:
            if record.number_copies_pickings < 0:
                raise ValidationError(
                    _("The number of copies must be greater or equal to 0")
                )
