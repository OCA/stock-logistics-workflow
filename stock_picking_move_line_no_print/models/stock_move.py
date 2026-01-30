# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    display_in_report = fields.Boolean(
        default=True, help="Whether to show it or not to customers in delivery slips"
    )

    def _merge_moves_fields(self):
        # It's need for hide in delivery slip report merged lines
        # if a least one has display_in_report False
        vals = super()._merge_moves_fields()
        if not any(self.mapped("display_in_report")):
            vals.update({"display_in_report": False})
        return vals
