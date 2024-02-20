# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    planned_consumed_date = fields.Datetime(
        "Planned consumed date",
        related="order_id.commitment_date",
        help="The planned consumed date by customer.",
    )

    def _prepare_procurement_values(self, group_id=False):
        return {
            **super()._prepare_procurement_values(group_id=group_id),
            "planned_consumed_date": self.planned_consumed_date,
        }
