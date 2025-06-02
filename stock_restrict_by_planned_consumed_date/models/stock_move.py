# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_available_quantity(self, *args, **kwargs):
        self.ensure_one()
        return super(
            StockMove,
            self.with_context(
                restrict_planned_consumed_date=self.planned_consumed_date,
            ),
        )._get_available_quantity(*args, **kwargs)

    def _update_reserved_quantity(self, *args, **kwargs):
        return super(
            StockMove,
            self.with_context(
                restrict_planned_consumed_date=self.planned_consumed_date,
            ),
        )._update_reserved_quantity(*args, **kwargs)
