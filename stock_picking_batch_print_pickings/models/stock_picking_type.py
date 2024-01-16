# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    batch_print_pickings = fields.Boolean(
        "Print pickings from batch",
        help="Allow print all pickings from batch",
    )
    number_copies_pickings = fields.Integer(
        "Number of copies",
        help="Number of copies to print",
        compute="_compute_number_copies_pickings",
        store=True,
        readonly=False,
    )

    @api.constrains("number_copies_pickings")
    def _check_number_copies_pickings(self):
        for record in self:
            if record.number_copies_pickings < 0:
                raise ValidationError(
                    _("The number of copies must be greater or equal to 0")
                )

    @api.depends("batch_print_pickings")
    def _compute_number_copies_pickings(self):
        for record in self:
            if record.batch_print_pickings:
                record.number_copies_pickings = 1
            else:
                record.number_copies_pickings = 0
