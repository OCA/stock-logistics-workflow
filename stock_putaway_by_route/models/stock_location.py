# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @property
    def _putaway_strategies(self):
        strategies = super()._putaway_strategies
        return strategies + ["route_id"]
