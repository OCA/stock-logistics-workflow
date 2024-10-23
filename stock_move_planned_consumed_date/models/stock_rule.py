# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        return [*super()._get_custom_move_fields(), "planned_consumed_date"]
