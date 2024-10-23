# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    planned_consumed_date = fields.Datetime(
        "Planned consumed date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="This is the expected consumed/usage date of the product by the customer.",
    )

    def _prepare_procurement_values(self):
        return {
            **super()._prepare_procurement_values(),
            "planned_consumed_date": self.planned_consumed_date,
        }

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            *super()._prepare_merge_moves_distinct_fields(),
            "planned_consumed_date",
        ]
