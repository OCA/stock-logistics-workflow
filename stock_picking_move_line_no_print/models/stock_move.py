# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    display_in_report = fields.Boolean(
        default=True, help="Whether to show it or not to customers in delivery slips"
    )

    def _merge_moves_fields(self):
        # It's need for hide in delivery slip report merged lines
        # if a least one has display_in_report False
        vals = super()._merge_moves_fields()
        if self.filtered_domain([("display_in_report", "=", False)]):
            vals.update({"display_in_report": False})
        return vals

    @api.model
    @api.depends_context("display_in_report")
    def _search(self, domain, *args, **kwargs):
        if self.env.context.get("display_in_report"):
            domain = fields.Domain.AND(
                [domain, fields.Domain("display_in_report", "=", True)]
            )
        return super()._search(domain, *args, **kwargs)
