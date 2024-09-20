# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    restrict_expiration_date = fields.Date(
        string="Restrict Expiration date",
    )

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["restrict_expiration_date"] = self.restrict_expiration_date
        return vals

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("restrict_expiration_date")
        return distinct_fields

    def _get_available_quantity(self, *args, **kwargs):
        self.ensure_one()
        return super(
            StockMove,
            self.with_context(
                restrict_expiration_date=self.restrict_expiration_date,
            ),
        )._get_available_quantity(*args, **kwargs)

    def _update_reserved_quantity(self, *args, **kwargs):
        return super(
            StockMove,
            self.with_context(
                restrict_expiration_date=self.restrict_expiration_date,
            ),
        )._update_reserved_quantity(*args, **kwargs)
