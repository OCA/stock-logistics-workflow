# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    display_in_report = fields.Boolean(related="move_id.display_in_report")

    @api.model
    @api.depends_context("display_in_report")
    def _search(self, domain, *args, **kwargs):
        if self.env.context.get("display_in_report"):
            domain = fields.Domain.AND(
                [domain, fields.Domain("display_in_report", "=", True)]
            )
        return super()._search(domain, *args, **kwargs)

    def _get_aggregated_product_quantities(self, **kwargs):
        res = super()._get_aggregated_product_quantities(**kwargs)
        for key in res:
            res[key]["display_in_report"] = True
            if res[key]["move"]:
                res[key]["display_in_report"] = all(
                    res[key]["move"].mapped("display_in_report")
                )
        return res
